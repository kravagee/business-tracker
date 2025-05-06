from flask import Flask, redirect, render_template, request, url_for, flash
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
@app.route('/business/<int:id>', methods=['GET'])
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
    return render_template('business.html', user=current_user, business=biz, workers=workers, products=products, managers=managers)


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
