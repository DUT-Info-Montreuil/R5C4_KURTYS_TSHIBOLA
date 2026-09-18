import os

from flask import Flask


# Chemin vers la base SQLite. Modifie-le si parties.db n'est pas à la racine du projet.
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "parties.db"))


def create_app():
    app = Flask(__name__)
    app.config["DB_PATH"] = os.path.abspath(DB_PATH)

    from app.controllers.parties_controller import parties_bp
    app.register_blueprint(parties_bp, url_prefix="/api/v1")

    return app
