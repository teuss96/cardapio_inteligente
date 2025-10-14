from flask import Blueprint, jsonify

sensores_bp = Blueprint("sensores", __name__)

@sensores_bp.route("/sensores", methods=["GET"])
def get_sensores():
    return jsonify({"mensagem": "Sensores funcionando!"})
