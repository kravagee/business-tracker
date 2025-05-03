import flask
from flask import request, make_response, jsonify

from data import db_session
from data.business import Business
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
            return make_response(jsonify({'error': 'Miss api key'}))
        db_sess = db_session.create_session()
        api_key = db_sess.query(User).filter(User.id == args[0]).one().api_key
        if api_key != kwargs['api_key']:
            return make_response(jsonify({'error': 'Invalid api key'}))
        return func(*args, **kwargs)

    return wrapper


@api_key_check
@blueprint.route('/api/business/add_manager/<id>', methods=['POST'])
def add_manager():
    pass


@api_key_check
@blueprint.route('/api/business/delete_manager/<id>', methods=['DELETE'])
def delete_manager(id):
    pass


@api_key_check
@blueprint.route('/api/business/add_worker/<id>', methods=['POST'])
def add_worker(id):
    pass


@api_key_check
@blueprint.route('/api/business/edit_worker/<id>', methods=['PUT'])
def edit_worker(id):
    pass


@api_key_check
@blueprint.route('/api/business/delete_worker/<id>', methods=['DELETE'])
def delete_worker(id):
    pass


@api_key_check
@blueprint.route('/api/business/add_product/<id>', methods=['POST'])
def add_product(id):
    pass


@api_key_check
@blueprint.route('/api/business/edit_product/<id>', methods=['PUT'])
def edit_product(id):
    pass


@api_key_check
@blueprint.route('/api/business/delete_product/<id>', methods=['DELETE'])
def delete_product(id):
    pass


@api_key_check
@blueprint.route('/api/business/get_products/<id>', methods=['GET'])
def get_products(id):
    pass


@api_key_check
@blueprint.route('/api/business/get_product/<id>', methods=['GET'])
def get_product(id):
    pass


@api_key_check
@blueprint.route('/api/business/get_managers/<id>', methods=['GET'])
def get_managers(id):
    pass


@api_key_check
@blueprint.route('/api/business/get_manager/<id>', methods=['GET'])
def get_manager(id):
    db_sess = db_session.create_session()
    manag = db_sess.query(User).filter(User.id == id).one()
    if not manag:
        return make_response(jsonify({'error': 'Manager not found'}))
    return jsonify(
        {
            'manager':
                [item.to_dict(only=('name'))
                 for item in manag]
        }
    )


@api_key_check
@blueprint.route('/api/business/get_workers/<id>', methods=['GET'])
def get_workers(id):
    pass


@api_key_check
@blueprint.route('/api/business/get_worker/<id>', methods=['GET'])
def get_worker(id):
    db_sess = db_session.create_session()
    worker = db_sess.query(Worker).filter(Worker.id == id).one()
    if not worker:
        return make_response(jsonify({'error': 'Worker not found'}))
    return jsonify(
        {
            'worker':
                [item.to_dict(only=('name', 'surname', 'salary', 'position'))
                 for item in worker]
        }
    )
