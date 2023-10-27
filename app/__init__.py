from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

# Instance of SQLAlchemy for our database
db = SQLAlchemy(app)

# Instance of Migrate to track our db migrations
migrate = Migrate(app, db)

# Instance of LoginManager to handle authentication
# login = LoginManager(app)
# login.login_view = 'login'



from app.blueprints.api import api
app.register_blueprint(api)

from . import routes, models