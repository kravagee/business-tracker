from flask import Flask, redirect, render_template, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random
import string

# Импорт из папки data
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

# Функция для генерации API ключа
def generate_api_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Загрузка пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))

# Главная (стартовая)
@app.route('/')
def index():
    return render_template('index.html', user=current_user)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == username).first():
            flash('Пользователь с таким именем уже существует')
            return redirect('/register')

        # Создание API ключа
        api_key = generate_api_key()

        # Создаем пользователя
        user = User(
            username=username,
            api_key=api_key,
            role=role  # добавьте в модель User поле role
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()

        # Дополнительные поля в зависимости от роли
        if role == 'owner':
            business_name = request.form.get('business_name')
            business_description = request.form.get('business_description')
            # Создайте бизнес или сохраните эти данные по необходимости
            # Например, создадим бизнес сразу:
            if business_name:
                business = Business(
                    name=business_name,
                    description=business_description,
                    owner_id=user.id
                )
                db_sess.add(business)
        elif role == 'manager':
            manager_info = request.form.get('manager_info')
            # Можно сюда добавить сохранение данных менеджера

        db_sess.commit()
        login_user(user)
        return redirect('/home')

    return render_template('register.html')  # Страница с динамическими вопросами

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

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# Главная страница после авторизации
@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)

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
        # Владелец видит свои бизнесы
        businesses = db_sess.query(Business).filter(Business.owner_id == current_user.id).all()
    elif current_user.role == 'manager':
        # Менеджер может видеть бизнесы, где он менеджер
        businesses = current_user.business_manager_list
    else:
        # Другие роли
        businesses = []
    return render_template('business_list.html', user=current_user, businesses=businesses)

# Просмотр конкретного бизнеса
@app.route('/business/<int:id>')
@login_required
def business(id):
    db_sess = db_session.create_session()
    biz = db_sess.query(Business).get(id)
    if not biz:
        return 'Бизнес не найден', 404
    # Проверка доступа
    if (current_user.role == 'owner' and biz.owner_id != current_user.id) and \
       (current_user.role == 'manager' and current_user not in biz.managers):
        return 'Доступ запрещен', 403
    workers = biz.worker_list
    products = biz.product_list
    managers = biz.manager_list
    return render_template('business.html', user=current_user, business=biz, workers=workers, products=products, managers=managers)

if __name__ == '__main__':
    db_session.global_init('db/tracker.db')
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(business_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
