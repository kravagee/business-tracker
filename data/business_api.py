import json
from functools import wraps

import flask
from flask import request, make_response, jsonify

from . import db_session
from .business import Business
from .product import Product
from .stats_business import StatsBusiness
from .user import User
from .worker import Worker

blueprint = flask.Blueprint(
    'business_api',
    __name__,
    template_folder='templates'
)


def api_key_check_business(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        us_ap_k = request.args.get('api_key')
        if not us_ap_k:
            return make_response(jsonify({'error': 'Miss api key'}), 400)
        db_sess = db_session.create_session()
        us = db_sess.query(Business).filter(Business.id == kwargs['biz_id']).first()
        if us.manager_list:
            m_l = json.loads(us.manager_list)
        else:
            m_l = {'id': []}

        api_key = db_sess.query(User).filter(User.id == us.owner_id or User.id.in_(us.manager_list['id'])).all()
        db_sess.close()
        for i in api_key:
            if i.api_key == us_ap_k:
                return func(*args, **kwargs)
        return make_response(jsonify({'error': 'Invalid api key'}), 403)
    return wrapper


@blueprint.route('/api/business/get_stat_business/<biz_id>', methods=['GET'])
@api_key_check_business
def get_business_stats(biz_id):
    db_sess = db_session.create_session()
    stats = db_sess.query(StatsBusiness).filter(StatsBusiness.id == biz_id).first()
    db_sess.close()
    if not stats:
        return make_response(jsonify({'error': 'User not found'}))
    return jsonify(
        {
            'stats':
                stats.to_dict(only=('bought_products', 'money_spent', 'worker_count'))
        }
    )


@blueprint.route('/api/business/<biz_id>/add_manager/<id>', methods=['POST'])
@api_key_check_business
def add_manager(biz_id, id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == int(biz_id)).first()
    id = int(id)
    if not bus:
        db_sess.close()
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.manager_list:
        man_list = {'id': [id]}
        bus.manager_list = json.dumps(man_list)
    else:
        man_list = json.loads(bus.manager_list)
        if not id in man_list['id']:
            man_list['id'].append(id)
            bus.manager_list = json.dumps(man_list)
        else:
            db_sess.close()
            return make_response(jsonify({'error': 'Manager already added'}), 400)

    man = db_sess.query(User).filter(User.id == id).first()
    if man.business_manager_list:
        m_l = json.loads(man.business_manager_list)
        m_l['id'].append(int(biz_id))
    else:
        m_l = dict()
        m_l['id'] = [int(biz_id)]
    man.business_manager_list = json.dumps(m_l)

    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Manager added'}), 200)


@blueprint.route('/api/business/<biz_id>/delete_manager/<id>', methods=['DELETE'])
@api_key_check_business
def delete_manager(biz_id, id):
    db_sess = db_session.create_session()
    biz_id, id = int(biz_id), int(id)
    bus = db_sess.query(Business).filter(Business.id == biz_id).first()
    if not bus:
        db_sess.close()
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.manager_list or len(json.loads(bus.manager_list)['id']) == 0:
        db_sess.close()
        return make_response(jsonify({'error': 'No managers linked to this business'}), 400)
    if id in json.loads(bus.manager_list)['id']:
        man_l = json.loads(bus.manager_list)
        man_l['id'].remove(id)
        bus.manager_list = json.dumps(man_l)

        us = db_sess.query(User).filter(User.id == id).first()
        m_l = json.loads(us.business_manager_list)
        m_l['id'].remove(biz_id)
        us.business_manager_list = json.dumps(m_l)
    else:
        return make_response(jsonify({'error': 'This manager does not linked to this business'}), 400)
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Manager deleted'}), 200)


@blueprint.route('/api/business/<biz_id>/edit_worker/<id>', methods=['PUT'])
@api_key_check_business
def edit_worker(biz_id, id):
    biz_id, id = int(biz_id), int(id)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    if not all([True if i in ['surname', 'name', 'salary', 'position'] else False
                for i in request.json]):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.id == id).first()
    if not worker:
        return make_response(jsonify({'error': 'Worker not found'}, 404))
    worker.surname = request.json['surname'] if 'surname' in request.json.keys() else worker.surname
    worker.name = request.json['name'] if 'name' in request.json.keys() else worker.name
    worker.position = request.json['position'] if 'position' in request.json.keys() else worker.position
    worker.salary = request.json['salary'] if 'salary' in request.json.keys() else worker.salary
    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Worker edited'}), 200)


@blueprint.route('/api/business/<biz_id>/delete_worker/<id>', methods=['DELETE'])
@api_key_check_business
def delete_worker(biz_id, id):
    biz_id, id = int(biz_id), int(id)
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == id).first()
    if not bus:
        db_sess.close()
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if not bus.worker_list or len(json.loads(bus.worker_list)['id']) == 0:
        db_sess.close()
        return make_response(jsonify({'error': 'No workers linked to this business'}), 400)
    if id in json.loads(bus.worker_list)['id']:
        wo_l = json.loads(bus.worker_list)
        wo_l['id'].remove(id)
        bus.worker_list = json.dumps(wo_l)
    else:
        db_sess.close()
        return make_response(jsonify({'error': 'This worker does not linked to this business'}), 400)

    stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz_id).first()
    stat.worker_count -= 1

    work = db_sess.query(Worker).filter(Worker.id == id).first()
    db_sess.delete(work)

    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Worker deleted'}), 200)


@blueprint.route('/api/business/<biz_id>/edit_product/<id>', methods=['PUT'])
@api_key_check_business
def edit_product(biz_id, id):
    biz_id, id = int(biz_id), int(id)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    if not all([True if i in ['status', 'name', 'price'] else False
                for i in request.json]):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if not product:
        db_sess.close()
        return make_response(jsonify({'error': 'Product not found'}, 404))
    if 'status' in request.json.keys():
        if request.json['status'] not in ['На складе', 'Использован', 'Доставляется']:
            db_sess.close()
            return make_response(jsonify({'error': 'Bad status'}), 400)
    product.status = request.json['status'] if 'status' in request.json.keys() else product.status
    product.name = request.json['name'] if 'name' in request.json.keys() else product.name

    if 'price' in request.json.keys():
        stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz_id).first()
        stat.money_spent -= product.price
        stat.money_spent += request.json['price']

    product.price = request.json['price'] if 'price' in request.json.keys() else product.price

    db_sess.commit()
    db_sess.close()
    return make_response(jsonify({'success': 'Product edited'}), 200)


@blueprint.route('/api/business/get_products/<biz_id>', methods=['GET'])
@api_key_check_business
def get_products(biz_id):
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == biz_id).first()
    if not bus:
        db_sess.close()
        return make_response(jsonify({'error': 'Business not found'}), 404)
    db_sess = db_session.create_session()
    if bus.product_list:
        products = db_sess.query(Product).filter(Product.id.in_(json.loads(bus.product_list)['id'])).all()
        db_sess.close()
        return jsonify(
            {
                'products':
                    [item.to_dict(only=('name', 'status', 'price'))
                     for item in products]
            }
        )
    db_sess.close()
    return make_response(jsonify({'error': 'There is not any product'}), 404)


@blueprint.route('/api/business/<biz_id>/get_product/<id>', methods=['GET'])
@api_key_check_business
def get_product(biz_id, id):
    id = int(id)
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if not product:
        db_sess.close()
        return make_response(jsonify({'error': 'Product not found'}), 404)
    db_sess.close()
    return jsonify(
        {
            'product':
                product.to_dict(only=('name', 'status', 'price'))
        }
    )


@blueprint.route('/api/business/get_workers/<biz_id>', methods=['GET'])
@api_key_check_business
def get_workers(biz_id):
    biz_id = int(biz_id)
    db_sess = db_session.create_session()
    bus = db_sess.query(Business).filter(Business.id == biz_id).first()
    if not bus:
        db_sess.close()
        return make_response(jsonify({'error': 'Business not found'}), 404)
    if bus.worker_list:
        workers = db_sess.query(Worker).filter(Worker.id.in_(json.loads(bus.worker_list)['id'])).all()
        db_sess.close()
        return jsonify(
            {
                'workers':
                    [item.to_dict(only=('name', 'surname', 'salary', 'position'))
                     for item in workers]
            }
        )
    db_sess.close()
    return make_response(jsonify({'error': 'There is not any worker'}), 404)


@blueprint.route('/api/business/<biz_id>/get_worker/<id>', methods=['GET'])
@api_key_check_business
def get_worker(biz_id, id):
    id = int(id)
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.id == id).first()
    if not worker:
        db_sess.close()
        return make_response(jsonify({'error': 'Worker not found'}), 404)
    db_sess.close()
    return jsonify(
        {
            'worker':
                worker.to_dict(only=('name', 'surname', 'salary', 'position'))
        }
    )


@blueprint.route('/api/business/<biz_id>/create_worker', methods=['POST'])
@api_key_check_business
def create_worker(biz_id):
    biz_id = int(biz_id)
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

    biz = db_sess.query(Business).filter(Business.id == biz_id).first()
    if biz.worker_list:
        wo_l = json.loads(biz.worker_list)
        wo_l['id'].append(worker.id)
    else:
        wo_l = dict()
        wo_l['id'] = [worker.id]

    biz.worker_list = json.dumps(wo_l)

    stat = db_sess.query(StatsBusiness).filter(StatsBusiness.business_id == biz_id).first()
    stat.worker_count += 1
    db_sess.commit()
    db_sess.close()

    return jsonify({'id': worker.id})
