from database import db
from main import app

db.init_app(app)

# Import anything using models after the database has connected the app instance
import models
import routes
import api
routes.apply_routes(app)
api.apply_routes(app)
