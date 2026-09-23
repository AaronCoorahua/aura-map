"""App factory de AuraMap."""
from flask import Flask

from app.config import Config
from app.db import create_tables, db, wait_for_db
from app.routes import battles_bp
from app.seed import seed_battles


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    wait_for_db(app)
    create_tables(app)
    app.register_blueprint(battles_bp)

    @app.cli.command("seed")
    def seed():
        """Carga 3 batallas de ejemplo en Lima si la DB está vacía."""
        insertadas = seed_battles()
        print(f"Batallas de ejemplo insertadas: {insertadas}")

    @app.get("/health")
    def health():
        return {"status": "ok", "version": app.config["APP_VERSION"]}

    return app
