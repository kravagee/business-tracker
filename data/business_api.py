from crypt import methods

import flask
from flask import request, make_response, jsonify

from data import db_session
from data.business import Business
from data.user import User

blueprint = flask.Blueprint(
    'business_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/business/add_manager/<id:int>', methods=['POST'])
def add_manager():
    pass


@blueprint.route('/api/business/delete_manager/<id:int>', methods=['DELETE'])
def delete_manager(id):
    pass


@blueprint.route('/api/business/add_worker/<id:int>', methods=['POST'])
def add_worker(id):
    pass


@blueprint.route('/api/business/edit_worker/<id:int>', methods=['PUT'])
def edit_worker(id):
    pass


@blueprint.route('/api/business/delete_worker/<id:int>', methods=['DELETE'])
def delete_worker(id):
    pass


@blueprint.route('/api/business/add_product/<id:int>', methods=['POST'])
def add_product(id):
    pass


@blueprint.route('/api/business/edit_product/<id:int>', methods=['PUT'])
def edit_product(id):
    pass


@blueprint.route('/api/business/delete_product/<id:int>', methods=['DELETE'])
def delete_product(id):
    pass


@blueprint.route('/api/business/get_products/<id:int>', methods=['GET'])
def get_products(id):
    pass


@blueprint.route('/api/business/get_product/<id:int>', methods=['GET'])
def get_product(id):
    pass


@blueprint.route('/api/business/get_managers/<id:int>', methods=['GET'])
def get_managers(id):
    pass


@blueprint.route('/api/business/get_manager/<id:int>', methods=['GET'])
def get_manager(id):
    pass


@blueprint.route('/api/business/get_workers/<id:int>', methods=['GET'])
def get_workers(id):
    pass


@blueprint.route('/api/business/get_worker/<id:int>', methods=['GET'])
def get_worker(id):
    pass