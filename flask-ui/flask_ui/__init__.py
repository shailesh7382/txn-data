from pathlib import Path
from flask import Flask
from .config import DevConfig, ProdConfig, TestConfig
from .extensions import db
from . import views
import os

def create_app(config_object=None):
    """
    Create and configure the Flask application.
    Pass config_object (class or import path) to override defaults.
    """
    # compute project-level templates directory (project_root/templates)
    project_root = Path(__file__).resolve().parents[1]
    templates_dir = project_root / "templates"

    # instantiate Flask with an explicit templates folder so Jinja can find your templates
    app = Flask(__name__, template_folder=str(templates_dir), instance_relative_config=True)

    # choose config: explicit, env override, fallback to DevConfig
    if config_object:
        app.config.from_object(config_object)
    else:
        cfg = os.getenv("FLASK_CONFIG", "dev").lower()
        if cfg == "prod":
            app.config.from_object(ProdConfig)
        elif cfg == "test":
            app.config.from_object(TestConfig)
        else:
            app.config.from_object(DevConfig)

    # init extensions
    db.init_app(app)

    # register routes
    views.register_routes(app)

    # optionally create tables (controlled by config)
    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()

    return app
