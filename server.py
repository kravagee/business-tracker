from flask import Flask, redirect
from flask_login import LoginManager, login_required, logout_user

from data import db_session, user_api, business_api
from data.business import Business
from data.product import Product
from data.user import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET'])
def index():
    '''
    Здесь необходимо вернуть стартовую страницу, с предложением зарегистрироваться или войт
    :return:
    '''
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Логика аутентификации пользователя в системе

    Обязательно использование функции login_user() из Flask-login
    :return:
    '''
    pass

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Логика регистрации пользователя в системе

    Важно! При создании пользователя необходимо продумать генерацию Api-ключа

    Обязательно использование функции login_user() из Flask-login

    :return:
    '''
    pass

'''

При написании дальнейших обработчиков обязателен декоратор login_required из flask-login,
а также, когда пользователю возвращается html-шаблон, необходимо в качестве аргумента передавать нынешнего пользователя


'''


@login_required
@app.route('/business/<id>/stats', methods=['GET', 'POST'])
def business_stats(id):
    pass


@login_required
@app.route('/business/<id>/products', methods=['GET', 'POST'])
def business_product(id):
    db_sess = db_session.create_session()
    buss = db_sess.query(Business).get(id)
    if not buss:
        return None
    products = db_sess.query(Product).filter(Product.id in buss.product_list).all()
    return None


@login_required
@app.route('/business/<id>/workers', methods=['GET', 'POST'])
def business_workers(id):
    db_sess = db_session.create_session()
    buss = db_sess.query(Business).get(id)
    if not buss:
        return None
    '''
    Должна быть логика с получением сотрудников
    '''
    return None


if __name__ == '__main__':
    db_session.global_init('db/tracker.db')
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(business_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
