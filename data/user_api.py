import json
from functools import wraps

import flask
from flask import request, make_response, jsonify

from . import db_session
from .business import Business
from .stats_business import StatsBusiness
from .stats_users import StatsUsers
from .user import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


def api_key_check_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        us_ap_k = request.args.get('api_key')
        if not us_ap_k:
            return make_response(jsonify({'error': 'Miss api key'}), 400)
        db_sess = db_session.create_session()
        api_key = db_sess.query(User).filter(User.id == kwargs['id']).first().api_key
        db_sess.close()
        if api_key != us_ap_k:
            return make_response(jsonify({'error': 'Invalid api key'}), 403)
        return func(*args, **kwargs)

    return wrapper


@blueprint.route('/api/users/get_stat_user/<id>', methods=['GET'])
@api_key_check_user
def get_user_stats(id):
    db_sess = db_session.create_session()
    stats = db_sess.query(StatsUsers).filter(StatsUsers.id == id).first()
    db_sess.close()
    if not stats:
        return make_response(jsonify({'error': 'User not found'}))
    return jsonify(
        {
            'stats':
                stats.to_dict(only=('business_count', 'business_management_count'))
        }
    )


@blueprint.route('/api/users/<id>/add_business', methods=['POST'])
@api_key_check_user
def add_business(id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    elif not all(key in request.json for key in ['name', 'description']):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    new_busin = Business()
    new_busin.name = request.json['name']
    new_busin.description = request.json['description']
    new_busin.owner_id = id
    db_sess.add(new_busin)
    db_sess.commit()

    us = db_sess.query(User).filter(User.id == id).first()
    if us.business_owner_list:
        own_l = json.loads(us.business_owner_list)
        own_l['id'].append(new_busin.id)
    else:
        own_l = dict()
        own_l['id'] = [new_busin.id]
    us.business_owner_list = json.dumps(own_l)

    stat_us = db_sess.query(StatsUsers).filter(StatsUsers.user_id == id).first()
    stat_us.business_count += 1

    bis_stat = StatsBusiness()
    bis_stat.business_id = new_busin.id
    bis_stat.worker_count = 0
    bis_stat.money_spent = 0
    bis_stat.bought_products = 0

    db_sess.add(bis_stat)

    db_sess.commit()
    db_sess.close()
    return {'ok': 'success'}


@blueprint.route('/api/users/get_businesses/<id>', methods=['GET'])
@api_key_check_user
def get_businesses(id):
    db_sess = db_session.create_session()
    us = db_sess.query(User).filter(User.id == id).first()
    own_l = dict()
    own_l['id'] = []
    if us.business_owner_list:
        own_l = json.loads(us.business_owner_list)
    if not own_l:
        db_sess.close()
        return make_response(jsonify({'error': 'User not found or User have zero businesses'}), 400)
    businesses = db_sess.query(Business).filter(Business.id.in_(own_l['id'])).all()
    db_sess.close()
    return jsonify(
        {
            'businesses':
                [item.to_dict(only=('name', 'description'))
                 for item in businesses]
        }
    )
