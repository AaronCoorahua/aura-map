"""App factory de AuraMap."""
from flask import Flask

from app.config import Config
from app.db import db


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": app.config["APP_VERSION"]}

    return app
