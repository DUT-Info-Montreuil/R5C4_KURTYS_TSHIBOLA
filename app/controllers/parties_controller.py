from flask import Blueprint, jsonify, request, current_app

from app.repositories.parties_repository import PartiesRepository
from app.services.parties_service import PartiesService, ValidationError

parties_bp = Blueprint("parties", __name__)


def _get_service():
    repository = PartiesRepository(current_app.config["DB_PATH"])
    return PartiesService(repository)


@parties_bp.route("/parties", methods=["GET"])
def get_parties():
    service = _get_service()
    try:
        resultat = service.lister_parties(request.args)
        return jsonify(resultat), 200
    except ValidationError as e:
        return jsonify({"erreur": e.message}), 400


@parties_bp.route("/parties/referentiel", methods=["GET"])
def get_referentiel():
    service = _get_service()
    return jsonify(service.referentiel()), 200
