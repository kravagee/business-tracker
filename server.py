from os import access
from pathlib import Path

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


def count_files(directory):
    path = Path(directory)
    return sum(1 for item in path.iterdir() if item.is_file())


# Загрузка юзера по ID
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))


# 1) Домашняя страница
@app.route('/', methods=['GET'])
def index():
    # Стартовая страница с предложением регистрации или входа
    return render_template('index.html', user=current_user)


# 2) Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.username == username).first():
            flash('Пользователь с таким именем уже существует')
            return redirect('/register')
        if db_sess.query(User).filter(User.email == email).first():
            flash('Пользователь с таким email уже существует')
            return redirect('/register')

        api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user = User(
            username=username,
            email=email,
            api_key=api_key
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/home')
    return render_template('register.html')


# 3) Вход (логин)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/home')
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('login.html')


# 4) Главная страница
@app.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)


# 5) Создать бизнес
@app.route('/create_business', methods=['GET', 'POST'])
@login_required
def create_business():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db_sess = db_session.create_session()
        # Создаем бизнес
        business = Business(
            name=name,
            description=description,
            owner_id=current_user.id
        )
        db_sess.add(business)
        db_sess.commit()
        flash('Бизнес успешно создан')
        return redirect('/business_list')
    return render_template('create_business.html', user=current_user)


# 6) Просмотр списка бизнесов
@app.route('/business_list', methods=['GET'])
@login_required
def business_list():
    db_sess = db_session.create_session()
    # Получаем бизнесы текущего пользователя
    businesses = db_sess.query(Business).filter(Business.owner_id == current_user.id).all()
    return render_template('business_list.html', user=current_user, businesses=businesses)


# 7) Смотреть топ пользователей и бизнесов
@app.route('/top', methods=['GET'])
@login_required
def top():
    db_sess = db_session.create_session()
    top_users = db_sess.query(User).order_by(User.rating.desc()).limit(10).all()
    top_biz = db_sess.query(Business).order_by(Business.rating.desc()).limit(10).all()
    return render_template('top.html', user=current_user, top_users=top_users, top_biz=top_biz)


# 8) Посмотреть бизнес по id
@app.route('/business/<int>', methods=['GET'])
@login_required
def business(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).get(id)
    if not biz:
        return 'Бизнес не найден', 404
    # Получение связанных списков
    workers = biz.worker_list  # необходимо, чтобы в модели были связи
    products = biz.product_list
    managers = biz.manager_list
    return render_template('business.html', user=current_user, business=biz, workers=workers, products=products,
                           managers=managers)


@app.route('/business/<id>/stats', methods=['GET'])
@login_required
def business_stats(id):
    db_sess = db_session.create_session()
    st_biz = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == id).one()
    biz = db_sess.query(Business).filter(Business.id == id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('business_stats.html', user=current_user, stats=st_biz, access=False)
    return render_template('business_stats.html', user=current_user, stats=st_biz, access=True)


@app.route('/business/<id>/products', methods=['GET'])
@login_required
def business_products(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).one()
    prods = db_sess.query(Product).filter(Product.id in Business.product_list['id']).all()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('business_products.html', user=current_user, purchases=prods, access=False)
    return render_template('business_products.html', user=current_user, purchases=prods, access=True)


@app.route('/business/<biz_id>/edit_product/<id>', methods=['GET', 'POST'])
@login_required
def edit_product(biz_id, id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).one()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('edit_product.html', user=current_user, bizz_id=biz_id, access=False)
    if request.method == 'GET':
        return render_template('edit_product.html', user=current_user, purchase=product, bizz_id=biz_id, access=True)
    product.name = request.form['name']
    product.status = request.form['status']
    image = request.form['image']
    img_path = './static/images/' + image.filename
    image.save(img_path)
    product.image = img_path
    product.price = request.form['price']
    db_sess.commit()
    db_sess.close()
    return render_template('edit_product.html', user=current_user, bizz_id=biz_id, purchase=product, access=True)


@app.route('/business/<id>/workers/', methods=['GET', 'POST'])
@login_required
def business_workers(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).one()
    workers = db_sess.query(Worker).filter(Worker.id in Business.worker_list['id']).all()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('business_workers.html', user=current_user, employees=workers, bizz_id=id, access=False)
    return render_template('business_workers.html', user=current_user, employees=workers, bizz_id=id, access=True)


@app.route('/business/<id>/add_worker', methods=['GET', 'POST'])
@login_required
def business_add_worker(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('add_worker.html', user=current_user, biz=biz, access=False)
    if request.method == 'GET':
        return render_template('add_worker.html', user=current_user, biz=biz, access=True)
    new_work = Worker()
    new_work.business_id = id
    new_work.name = request.form['name']
    new_work.surname = request.form['surname']
    new_work.salary = request.form['salary']
    new_work.position = request.form['position']
    db_sess.add(new_work)
    db_sess.commit()
    db_sess.close()
    return render_template('add_worker.html', user=current_user, access=True, biz=biz)


@app.route('/business/<biz_id>/edit_worker/<id>', methods=['GET', 'POST'])
@login_required
def business_edit_worker(biz_id, id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    work = db_sess.query(Worker).filter(Worker.id == id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('edit_worker.html', user=current_user, work=work, biz=biz, access=False)
    if request.method == 'GET':
        return render_template('edit_worker.html', biz=biz, user=current_user, access=True, work=work)
    work.name = request.form['name']
    work.surname = request.form['surname']
    work.salary = request.form['salary']
    work.position = request.form['position']
    db_sess.commit()
    return render_template('edit_worker.html', biz=biz, user=current_user, access=True, work=work)


@app.route('/business/<biz_id>/delete_worker/<id>', methods=['POST'])
@login_required
def business_delete_worker(biz_id, id):
    db_sess = db_session.create_session()
    work = db_sess.query(Worker).filter(Worker.id == id).one()
    biz = db_sess.query(Business).filter(Business.id == id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return make_response(jsonify({'error': 'Access Denied'}), 403)
    db_sess.delete(work)
    db_sess.commit()
    db_sess.close()
    return redirect(url_for('business_workers', id=biz_id))


@app.route('/business/<biz_id>/add_product', methods=['GET', 'POST'])
@login_required
def business_add_product(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=False)
    if request.method == 'GET':
        return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=True)
    new_prod = Product()
    new_prod.name = request.form['name']
    new_prod.status = request.form['status']
    image = request.form['image']
    img_path = './static/images/' + image.filename
    image.save(img_path)
    new_prod.image = img_path
    new_prod.price = request.form['price']
    db_sess.add(new_prod)
    db_sess.commit()
    db_sess.close()
    return render_template('add_product.html', user=current_user, bizz_id=biz_id, access=True)


@app.route('/business/<biz_id>/manager_list', methods=['GET'])
@login_required
def business_manager_list(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    managers = db_sess.query(User).filter(User.id in Business.manager_list['id']).all()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('business_managers.html', user=current_user, managers=managers, bizz_id=biz_id,
                               access=False)
    return render_template('business_managers.html', user=current_user, managers=managers, bizz_id=biz_id, access=True)


@app.route('/business/<biz_id>/add_manager', methods=['GET', 'POST'])
@login_required
def business_add_manger(biz_id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return render_template('add_manager.html', user=current_user, access=False)
    if request.method == 'GET':
        return render_template('add_manager.html', user=current_user, access=True)
    manag = db_sess.query(User).filter(User.username == request.form['manag_username']).one()
    biz.manager_list['id'].append(manag.id)
    return render_template('add_manager.html', user=current_user, access=True)


@app.route('/business/<biz_id>/remove_manager/<id>', methods=['POST'])
def business_remove_manager(biz_id, id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).filter(Business.id == biz_id).one()
    if biz.owner_id != current_user.id or current_user.id not in biz.manager_list['id'] or not biz:
        return make_response(jsonify({'error': 'Access denied'}), 403)
    biz.manager_list['id'].remove(id)
    db_sess.commit()
    db_sess.close()
    return redirect(url_for('business_manager_list', biz_id=biz_id))


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
