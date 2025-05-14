import json

from flask import Flask, redirect, render_template, request, url_for, flash, make_response, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random
import string

from data import db_session, user_api, business_api
from data.user import User
from data.business import Business
from data.worker import Worker
from data.product import Product
from data.stats_business import StatsBusiness
from data.stats_users import StatsUsers

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def generate_api_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Загрузка юзера по ID
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/')
def index():
    if not current_user:
        return render_template('index.html')
    return render_template('index.html', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        password = request.form['password']
        db_sess = db_session.create_session()

        # Создаём пользователя
        user = User()
        if db_sess.query(User).filter(User.username == username).first():
            return render_template('register.html')
        user.username = username
        user.set_password(password)
        user.api_key = generate_api_key()

        db_sess.add(user)
        db_sess.commit()

        stats = StatsUsers()
        stats.user_id = user.id
        stats.business_count = 0
        stats.business_managering_count = 0
        db_sess.add(stats)

        db_sess.commit()
        login_user(user)
        db_sess.close()
        return redirect('/home')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            login_user(user)
            db_sess.close()
            return redirect('/home')
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('login.html')


@app.route('/home')
@login_required
def home():
    db_sess = db_session.create_session()
    stats = db_sess.query(StatsUsers).filter(StatsUsers.user_id == current_user.id).first()
    db_sess.close()
    return render_template('home_owner.html', user=current_user, stats=stats)


@app.route('/create_business', methods=['GET', 'POST'])
@login_required
def create_business():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db_sess = db_session.create_session()

        business = Business(
            name=name,
            description=description,
            owner_id=current_user.id
        )
        db_sess.add(business)
        db_sess.commit()

        us = db_sess.query(User).filter(User.id == current_user.id).first()

        if us.business_owner_list:
            list_biz = json.loads(us.business_owner_list)
            list_biz['id'].append(business.id)
            us.business_owner_list = json.dumps(list_biz)
            db_sess.commit()
        else:
            list_biz = dict()
            list_biz['id'] = [business.id]
            us.business_owner_list = json.dumps(list_biz)
            db_sess.commit()

        # Создаем статистику для бизнеса
        biz_stats = StatsBusiness(
            business_id=business.id,
            bought_products=0,
            money_spent=0,
            worker_count=0
        )
        db_sess.add(biz_stats)

        # Обновляем статистику пользователя
        user_stats = db_sess.query(StatsUsers).filter(StatsUsers.user_id == current_user.id).first()
        if user_stats:
            user_stats.business_count += 1

        db_sess.commit()
        flash('Бизнес успешно создан')
        db_sess.close()
        return redirect('/business_list')
    return render_template('create_business.html')


# Просмотр своих бизнесов
@app.route('/business_list')
@login_required
def business_list():
    db_sess = db_session.create_session()
    bizes = []
    if current_user.business_manager_list and current_user.business_owner_list:
        bizes = json.loads(current_user.business_owner_list)['id'] + json.loads(current_user.business_manager_list)[
            'id']
    elif current_user.business_manager_list:
        bizes = json.loads(current_user.business_manager_list)['id']
    elif current_user.business_owner_list:
        bizes = json.loads(current_user.business_owner_list)['id']
    businesses_with_stats = []
    for biz in bizes:
        stats = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz).first()
        businesses_with_stats.append((db_sess.query(Business).filter(Business.id == biz).first(), stats))
    db_sess.close()
    return render_template('business_list.html',
                           user=current_user,
                           businesses=businesses_with_stats)


# Просмотр конкретного бизнеса
@app.route('/business/<int:id>')
@login_required
def business(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).first()
    if not biz:
        flash('Бизнес не найден')
        db_sess.close()
        return redirect('/business_list')
    workers = db_sess.query(Worker).filter(Worker.business_id == id).all()
    products = db_sess.query(Product).filter(Product.business_id == id).all()
    mans = dict()
    mans['id'] = []
    if biz.manager_list:
        mans = json.loads(biz.manager_list)

    managers = db_sess.query(User).filter(User.id.in_(mans['id'])).all()
    stats = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == id).first()

    db_sess.close()

    return render_template('business.html',
                           user=current_user,
                           business=biz,
                           workers=workers,
                           products=products,
                           managers=managers,
                           stats=stats)


# Топ пользователей/бизнесов
@app.route('/top')
@login_required
def top():
    db_sess = db_session.create_session()

    # Топ пользователей по количеству бизнесов
    top_users = db_sess.query(User, StatsUsers).join(StatsUsers).order_by(StatsUsers.business_count.desc()).limit(
        10).all()

    # Топ бизнесов по количеству работников
    top_businesses = db_sess.query(Business, StatsBusiness).join(StatsBusiness).order_by(
        StatsBusiness.worker_count.desc()).limit(10).all()

    db_sess.close()

    return render_template('top.html',
                           user=current_user,
                           top_users=top_users,
                           top_businesses=top_businesses)


@app.route('/business/<id>/stats', methods=['GET'])
@login_required
def business_stats(id):
    db_sess = db_session.create_session()
    st_biz = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == id).first()
    biz = db_sess.query(Business).filter(Business.id == id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('business_stats.html', user=current_user, stats=st_biz, access=False)
    db_sess.close()
    return render_template('business_stats.html', user=current_user, stats=st_biz, access=True)


@app.route('/business/<id>/products', methods=['GET'])
@login_required
def business_products(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).first()
    prods = db_sess.query(Product).filter(Product.business_id == biz.id).all()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('business_products.html', user=current_user, bizz_id=biz.id, purchases=prods,
                               access=False)
    db_sess.close()
    return render_template('business_products.html', user=current_user, bizz_id=biz.id, purchases=prods, access=True)


@app.route('/business/<biz_id>/edit_product/<id>', methods=['GET', 'POST'])
@login_required
def edit_product(biz_id, id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('edit_product.html', user=current_user, bizz_id=biz_id, access=False)
    if request.method == 'GET':
        db_sess.close()
        return render_template('edit_product.html', user=current_user, purchase=product, bizz_id=biz_id, access=True)
    product.name = request.form['name']
    product.status = request.form['status']
    image = request.files['image']
    img_path = 'images/' + image.filename
    image.save('static/' + img_path)
    product.image = img_path
    product.image = img_path
    product.price = request.form['price']
    db_sess.commit()
    db_sess.close()
    return render_template('edit_product.html', user=current_user, bizz_id=biz_id, purchase=product, access=True)


@app.route('/business/<id>/workers/', methods=['GET', 'POST'])
@login_required
def business_workers(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).first()
    workers = db_sess.query(Worker).filter(Worker.business_id == id).all()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('business_workers.html', user=current_user, employees=workers, bizz_id=id, access=False)
    db_sess.close()
    return render_template('business_workers.html', user=current_user, employees=workers, bizz_id=id, access=True)


@app.route('/business/<id>/add_worker', methods=['GET', 'POST'])
@login_required
def business_add_worker(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('add_worker.html', user=current_user, biz=biz, access=False)
    if request.method == 'GET':
        db_sess.close()
        return render_template('add_worker.html', user=current_user, biz=biz, access=True)
    new_work = Worker()
    new_work.business_id = id
    new_work.name = request.form['name']
    new_work.surname = request.form['surname']
    new_work.salary = request.form['salary']
    new_work.position = request.form['position']
    db_sess.add(new_work)
    db_sess.commit()

    if not biz.worker_list:
        wor = dict()
        wor['id'] = [new_work.id]
    else:
        wor = json.loads(biz.worker_list)
        wor['id'].append(new_work.id)
    biz.worker_list = json.dumps(wor)

    stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == id).first()
    stat.worker_count += 1

    db_sess.commit()
    db_sess.close()
    return render_template('add_worker.html', user=current_user, access=True, biz=biz)


@app.route('/business/<biz_id>/edit_worker/<id>', methods=['GET', 'POST'])
@login_required
def business_edit_worker(biz_id, id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    work = db_sess.query(Worker).filter(Worker.id == id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('edit_worker.html', user=current_user, work=work, biz=biz, access=False)
    if request.method == 'GET':
        db_sess.close()
        return render_template('edit_worker.html', biz=biz, user=current_user, access=True, work=work)
    work.name = request.form['name']
    work.surname = request.form['surname']
    work.salary = request.form['salary']
    work.position = request.form['position']
    db_sess.commit()
    db_sess.close()
    return render_template('edit_worker.html', biz=biz, user=current_user, access=True, work=work)


@app.route('/business/<biz_id>/delete_worker/<id>', methods=['POST', 'GET'])
@login_required
def business_delete_worker(biz_id, id):
    db_sess = db_session.create_session()
    work = db_sess.query(Worker).filter(Worker.id == id).first()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return make_response(jsonify({'error': 'Access Denied'}), 403)
    db_sess.delete(work)

    if biz.worker_list:
        wor = json.loads(biz.worker_list)
    else:
        wor = dict()
        wor['id'] = []
    if id in wor['id']:
        wor['id'].remove(id)
    biz.worker_list = json.dumps(wor)

    stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz_id).first()
    stat.worker_count -= 1

    db_sess.commit()
    db_sess.close()
    return redirect(url_for('business_workers', id=biz_id))


@app.route('/business/<biz_id>/add_product', methods=['GET', 'POST'])
@login_required
def business_add_product(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=False)
    if request.method == 'GET':
        db_sess.close()
        return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=True)
    new_prod = Product()
    new_prod.name = request.form['name']
    new_prod.status = request.form['status']
    image = request.files['image']
    img_path = 'images/' + image.filename
    image.save('static/' + img_path)
    new_prod.image = img_path
    new_prod.price = request.form['price']
    new_prod.business_id = biz_id
    db_sess.add(new_prod)
    db_sess.commit()

    if biz.product_list:
        pr_l = json.loads(biz.product_list)
        pr_l['id'].append(new_prod.id)
    else:
        pr_l = dict()
        pr_l['id'] = [new_prod.id]

    biz.product_list = json.dumps(pr_l)

    stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz_id).first()
    stat.bought_products += 1
    stat.money_spent += new_prod.price

    db_sess.commit()
    db_sess.close()
    return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=True)


@app.route('/business/<biz_id>/manager_list', methods=['GET'])
@login_required
def business_manager_list(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    managers = db_sess.query(User).filter(User.id.in_(man_list['id'])).all()
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('business_managers.html', user=current_user, managers=managers, bizz_id=biz_id,
                               access=False)
    db_sess.close()
    return render_template('business_managers.html', user=current_user, managers=managers, bizz_id=biz_id, access=True)


@app.route('/business/<biz_id>/add_manager', methods=['GET', 'POST'])
@login_required
def business_add_manager(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return render_template('add_manager.html', user=current_user, access=False)
    if request.method == 'GET':
        db_sess.close()
        return render_template('add_manager.html', user=current_user, access=True)
    manag = db_sess.query(User).filter(User.username == request.form['manag_username']).first()
    if not manag:
        db_sess.close()
        return render_template('add_manager.html', user=current_user, access=True)
    if manag.id not in man_list['id']:
        man_list['id'].append(manag.id)
    biz.manager_list = json.dumps(man_list)

    if manag.business_manager_list:
        mans_l = json.loads(manag.business_manager_list)
        mans_l['id'] = [biz.id]
    else:
        mans_l = dict()
        mans_l['id'] = [biz.id]
    manag.business_manager_list = json.dumps(mans_l)

    db_sess.commit()
    db_sess.close()
    return render_template('add_manager.html', user=current_user, access=True)


@app.route('/business/<biz_id>/remove_manager/<id>', methods=['POST', 'GET'])
@login_required
def business_remove_manager(biz_id, id):
    biz_id, id = int(biz_id), int(id)
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    man_list = {'id': []}
    if biz.manager_list:
        man_list = json.loads(biz.manager_list)
    if biz.owner_id != current_user.id and current_user.id not in man_list['id'] or not biz:
        db_sess.close()
        return make_response(jsonify({'error': 'Access denied'}), 403)
    man_list['id'].remove(id)
    us = db_sess.query(User).filter(User.id == id).first()
    mans_l = json.loads(us.business_manager_list)
    mans_l['id'].remove(biz_id)
    biz.manager_list = json.dumps(mans_l)
    us.business_manager_list = json.dumps(mans_l)
    db_sess.commit()
    db_sess.close()
    return redirect(url_for('business_manager_list', biz_id=biz_id))


@app.route('/api-docs', methods=['GET'])
@login_required
def docs_api():
    return render_template('api_docs.html', current_user=current_user)


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# Запуск сервера
if __name__ == '__main__':
    db_session.global_init('db/tracker.db')
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(business_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
