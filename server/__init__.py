from database import db
from main import app

db.init_app(app)

# Import anything using models after the database has connected the app instance
import models
import routes
from api import api_blueprint
routes.apply_routes(app)
app.register_blueprint(api_blueprint)
