from flask import session, request
from flask.views import MethodView
from models import User

class SessionAPI(MethodView):
    def post(self):
        json_data = request.get_json()

        if ('password' in json_data) and ('username' in json_data):
            user = User.query.filter_by(
                    username = json_data['username'],
                    password = json_data['password']
            ).first()

            if user is not None:
                session['username'] = json_data['username']
                return '', 200
            else:
                return 'error: no user found', 400

        return 'error: missing credentials', 400

    def delete(self):
        session.pop('username', None)
        return '', 200

def apply_routes(app):
    app.add_url_rule('/api/session', view_func = SessionAPI.as_view('sessions'))
