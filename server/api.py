from flask import Blueprint, session, request
from flask_restful import Api, Resource
from models import User

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

# Handles user logins and logouts
class Session(Resource):
    def post(self):
        json_data = request.get_json()
        if ('password' in json_data) and ('username') in json_data:
            user = User.query.filter_by(
                    username = json_data['password'],
                    password = json_data['username']
            ).first()

            if user is None:
                session['username'] = username
                return '', 200
            else:
                return '', 400

        return '', 400

    def delete():
        session.pop('username', None)
        return '', 200

api.add_resource(Session, '/api/session')
