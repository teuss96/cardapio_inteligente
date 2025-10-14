from flask import Blueprint, jsonify

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/produtos", methods=["GET"])
def get_sensores():
    return jsonify({"mensagem": "produtos funcionando!"})
