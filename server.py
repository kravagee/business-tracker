from os import write

from flask import Flask, redirect, render_template, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random
import string
from datetime import datetime

from data import db_session, user_api, business_api
from data.user import User
from data.business import Business
from data.worker import Worker
from data.product import Product
from data.stats_business import StatsBusiness
from data.stats_users import StatsUsers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def generate_api_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        password = request.form['password']
        business_name = request.form.get('business_name', 'Новый бизнес')

        db_sess = db_session.create_session()

        # Создаём пользователя
        user = User()
        user.username = username
        user.hashed_password = password
        user.api_key = generate_api_key()
        user.name = ""
        user.surname = ""
        user.email = ""
        user.position = "Владелец"
        user.set_password(password)

        db_sess.add(user)
        db_sess.flush()  # Чтобы получить ID пользователя

        # Создаём бизнес
        business = Business()
        business.name = business_name
        business.description = ""
        business.owner_id = user.id
        db_sess.add(business)

        # Статистика бизнеса
        biz_stats = StatsBusiness()
        biz_stats.business_id = business.id
        biz_stats.bought_products = 0
        biz_stats.money_spent = 0
        biz_stats.worker_count = 0
        db_sess.add(biz_stats)

        # Статистика пользователя
        stats = StatsUsers()
        stats.user_id = user.id
        stats.business_count = 1
        stats.business_managering_count = 0
        db_sess.add(stats)

        db_sess.commit()
        login_user(user)
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
            return redirect('/home')
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/home')
@login_required
def home():
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.user_id == current_user.id).first()

    if worker:
        return render_template('home_worker.html', user=current_user, worker=worker)
    else:
        stats = db_sess.query(StatsUsers).filter(StatsUsers.user_id == current_user.id).first()
        return render_template('home_owner.html', user=current_user, stats=stats)

# Создание бизнеса (для владельца)
@app.route('/create_business', methods=['GET', 'POST'])
@login_required
def create_business():
    if current_user.role != 'owner':
        flash('Доступ запрещен')
        return redirect('/home')

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
        return redirect('/business_list')

    return render_template('create_business.html')


# Просмотр своих бизнесов
@app.route('/business_list')
@login_required
def business_list():
    db_sess = db_session.create_session()
    if current_user.role == 'owner':
        businesses = db_sess.query(Business).filter(Business.owner_id == current_user.id).all()
    elif current_user.role == 'manager':
        businesses = db_sess.query(Business).join(Business.manager_list).filter(User.id == current_user.id).all()
    else:
        businesses = []

    # Получаем статистику для каждого бизнеса
    businesses_with_stats = []
    for biz in businesses:
        stats = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz.id).first()
        businesses_with_stats.append((biz, stats))

    return render_template('business_list.html',
                           user=current_user,
                           businesses=businesses_with_stats)


# Просмотр конкретного бизнеса
@app.route('/business/<int:id>')
@login_required
def business(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).get(id)
    if not biz:
        flash('Бизнес не найден')
        return redirect('/business_list')

    # Проверка доступа
    if current_user.role == 'owner' and biz.owner_id != current_user.id:
        flash('Доступ запрещен')
        return redirect('/business_list')

    if current_user.role == 'manager' and current_user not in biz.manager_list:
        flash('Доступ запрещен')
        return redirect('/business_list')

    workers = db_sess.query(Worker).filter(Worker.business_id == id).all()
    products = db_sess.query(Product).filter(Product.business_id == id).all()
    managers = biz.manager_list
    stats = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == id).first()

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

    return render_template('top.html',
                           user=current_user,
                           top_users=top_users,
                           top_businesses=top_businesses)


if __name__ == '__main__':
    db_session.global_init('db/tracker.db')
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(business_api.blueprint)
    app.run(port=8080, host='127.0.0.1')