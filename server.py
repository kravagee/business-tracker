from flask import Flask

from data import db_session, user_api, business_api
from data.business import Business
from data.product import Product

app = Flask(__name__)


@app.route('/business/<id:int>/stats', methods=['GET', 'POST'])
def business_stats(id):
    pass

@app.route('/business/<id:int>/products', methods=['GET', 'POST'])
def business_product(id):
    db_sess = db_session.create_session()
    buss = db_sess.query(Business).get(id)
    if not buss:
        return None
    products = db_sess.query(Product).filter(Product.id in buss.product_list).all()
    return None


@app.route('/business/<id:int>/workers', methods=['GET', 'POST'])
def business_product(id):
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