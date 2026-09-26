from flask import Flask

from app.extensions import db, migrate, login_manager
from .config import Config


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Load all models before Alembic initializes
    from app.models import User, Role
    from app.pilot.models import PilotRecord

    migrate.init_app(app, db)

    from app.main.routes import main
    from app.pilot.routes import pilot
    from app.auth.routes import auth

    app.register_blueprint(main)
    app.register_blueprint(pilot)
    app.register_blueprint(auth)

    return app
