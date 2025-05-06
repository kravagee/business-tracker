import flask
from flask import request, make_response, jsonify

from data import db_session
from data.business import Business
from data.product import Product
from data.user import User
from data.worker import Worker

blueprint = flask.Blueprint(
    'business_api',
    __name__,
    template_folder='templates'
)


def api_key_check(func):
    def wrapper(*args, **kwargs):
        if not 'api_key' in kwargs.keys():
            return make_response(jsonify({'error': 'Miss api key'}), 400)
        db_sess = db_session.create_session()
        us = db_sess.query(Business).filter(Business.id == args[0]).one()
        api_key = db_sess.query(User).filter(User.id == us.owner_id).one().api_key
        if api_key != kwargs['api_key']:
            return make_response(jsonify({'error': 'Invalid api key'}), 403)
        return func(*args, **kwargs)

    return wrapper


@api_key_check
@blueprint.route('/api/business/add_manager/<id>', methods=['POST'])
def add_manager(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.manager_list:
        bus.manager_list = {'id': [request.json['manager_id']]}
    else:
        if not id in bus.manager_list['id']:
            bus.manager_list['id'].append(request.json['manager_id'])
        else:
            return make_response(jsonify({'error': 'Manager already added'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Manager added'}), 200)


@api_key_check
@blueprint.route('/api/business/delete_manager/<id>', methods=['DELETE'])
def delete_manager(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.manager_list or len(bus.manager_list['id']) == 0:
        return make_response(jsonify({'error': 'No managers linked to this business'}), 400)
    if request.json['manager_id'] in bus.manager_list['id']:
        bus.manager_list['id'].remove(request.json['manager_id'])
    else:
        return make_response(jsonify({'error': 'This manager does not linked to this business'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Manager deleted'}), 200)


@api_key_check
@blueprint.route('/api/business/add_worker/<id>', methods=['POST'])
def add_worker(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.worker_list:
        bus.worker_list = {'id': [request.json['worker_id']]}
    else:
        if not request.json['worker_id'] in bus.worker_list['id']:
            bus.worker_list['id'].append(request.json['worker_id'])
        else:
            return make_response(jsonify({'error': 'This worker already added'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Worker added'}), 200)


@api_key_check
@blueprint.route('/api/business/edit_worker/<id>', methods=['PUT'])
def edit_worker(id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    if not all([True if i in ['surname', 'name', 'salary', 'position'] else False
                for i in request.json]):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.id == id).one()
    if not worker:
        return make_response(jsonify({'error': 'Worker not found'}, 404))
    worker.surname = request.json['surname'] if 'surname' in request.json.keys() else worker.surname
    worker.name = request.json['name'] if 'name' in request.json.keys() else worker.name
    worker.position = request.json['position'] if 'position' in request.json.keys() else worker.position
    worker.salary = request.json['salary'] if 'salary' in request.json.keys() else worker.salary
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Worker edited'}), 200)


@api_key_check
@blueprint.route('/api/business/delete_worker/<id>', methods=['DELETE'])
def delete_worker(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.worker_list or len(bus.worker_list['id']) == 0:
        return make_response(jsonify({'error': 'No workers linked to this business'}), 400)
    if request.json['worker_id'] in bus.worker_list['id']:
        bus.worker_list['id'].remove(request.json['worker_id'])
    else:
        return make_response(jsonify({'error': 'This worker does not linked to this business'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Worker deleted'}), 200)


@api_key_check
@blueprint.route('/api/business/add_product/<id>', methods=['POST'])
def add_product(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.product_list:
        bus.product_list = {'id': [request.json['product_id']]}
    else:
        bus.worker_list['id'].append(request.json['product_id'])
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Product added'}), 200)


@api_key_check
@blueprint.route('/api/business/edit_product/<id>', methods=['PUT'])
def edit_product(id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    if not all([True if i in ['status', 'name', 'image', 'price'] else False
                for i in request.json]):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).one()
    if not product:
        return make_response(jsonify({'error': 'Product not found'}, 404))
    product.status = request.json['status'] if 'status' in request.json.keys() else product.status
    product.name = request.json['name'] if 'name' in request.json.keys() else product.name
    product.image = request.json['image'] if 'image' in request.json.keys() else product.image
    product.price = request.json['price'] if 'price' in request.json.keys() else product.price
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Product edited'}), 200)


@api_key_check
@blueprint.route('/api/business/delete_product/<id>', methods=['DELETE'])
def delete_product(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.product_list or len(bus.product_list['id']) == 0:
        return make_response(jsonify({'error': 'No products linked to this business'}), 400)
    if request.json['product_id'] in bus.product_list['id']:
        bus.product_list['id'].remove(request.json['product_id'])
    else:
        return make_response(jsonify({'error': 'This product does not linked to this business'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Product deleted'}), 200)


@api_key_check
@blueprint.route('/api/business/get_products/<id>', methods=['GET'])
def get_products(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(Product.id in bus.product_list['id']).all()
    return jsonify(
        {
            'products':
                [item.to_dict(only=('name', 'description', 'status', 'price'))
                 for item in products]
        }
    )


@blueprint.route('/api/business/get_product/<id>', methods=['GET'])
def get_product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).one()
    return jsonify(
        {
            'product':
                product.to_dict(only=('name', 'description', 'status', 'price'))
        }
    )


@api_key_check
@blueprint.route('/api/business/get_managers/<id>', methods=['GET'])
def get_managers(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    db_sess = db_session.create_session()
    managers = db_sess.query(User).filter(User.id in bus.manager_list['id']).all()
    return jsonify(
        {
            'managers':
                [item.to_dict(only=('name'))
                 for item in managers]
        }
    )


@blueprint.route('/api/business/get_manager/<id>', methods=['GET'])
def get_manager(id):
    db_sess = db_session.create_session()
    manag = db_sess.query(User).filter(User.id == id).one()
    if not manag:
        return make_response(jsonify({'error': 'Manager not found'}), 404)
    return jsonify(
        {
            'manager':
                manag.to_dict(only=('name'))
        }
    )


@api_key_check
@blueprint.route('/api/business/get_workers/<id>', methods=['GET'])
def get_workers(id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).one()
    if not bus:
        return make_response(jsonify({'error': 'Business not found'}), 404)
    db_sess = db_session.create_session()
    workers = db_sess.query(Worker).filter(Worker.id in bus.worker_list['id']).all()
    return jsonify(
        {
            'workers':
                [item.to_dict(only=('name', 'surname', 'salary', 'position'))
                 for item in workers]
        }
    )


@blueprint.route('/api/business/get_worker/<id>', methods=['GET'])
def get_worker(id):
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.id == id).one()
    if not worker:
        return make_response(jsonify({'error': 'Worker not found'}), 404)
    return jsonify(
        {
            'worker':
                worker.to_dict(only=('name', 'surname', 'salary', 'position'))
        }
    )


@blueprint.route('/api/business/create_worker', methods=['POST'])
def create_worker():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['surname', 'name', 'position',
                                                 'salary']):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    worker = Worker(
        surname=request.json['surname'],
        name=request.json['name'],
        position=request.json['position'],
        salary=request.json['salary']
    )
    db_sess.add(worker)
    db_sess.commit()
    return jsonify({'id': worker.id})


@blueprint.route('/api/business/create_product', methods=['POST'])
def create_product():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['status', 'name', 'price',
                                                 'image']):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    product = Product(
        status=request.json['status'],
        name=request.json['name'],
        price=request.json['price'],
        image=request.json['image']
    )
    db_sess.add(product)
    db_sess.commit()
    return jsonify({'id': product.id})
