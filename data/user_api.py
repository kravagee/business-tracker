import flask
from flask import request, make_response, jsonify

from data import db_session
from data.business import Business
from data.user import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users/get_stat_user/<id:int>', methods=['GET'])
def get_user_stats(id):
    pass


@blueprint.route('/api/users/get_stat_business/<id:int>', methods=['GET'])
def get_business_stats(id):
    pass


@blueprint.route('/api/users/add_business/', methods=['POST'])
def add_business():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    elif not all(key in request.json for key in ['name', 'description']):
        return make_response(jsonify({'error': 'Bad request'}, 400))
    db_sess = db_session.create_session()
    new_busin = Business()
    new_busin.name = request.json['name']
    new_busin.description = request.json['description']
    db_sess.add(new_busin)
    db_sess.commit()
    db_sess.close()


@blueprint.route('/api/users/get_businesses/<id:int>', methods=['GET'])
def get_businesses(id):
    db_sess = db_session.create_session()
    business_ids = db_sess.query(User).filter(User.id == id).one()
    businesses = db_sess.query(Business).filter(Business.id in business_ids).all()
    return jsonify(
        {
            'businesses':
                [item.to_dict(only=('name', 'description'))
                 for item in businesses]
         }
    )
