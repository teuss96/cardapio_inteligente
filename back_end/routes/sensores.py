<<<<<<< HEAD
from flask import Blueprint, jsonify

sensores_bp = Blueprint("sensores", __name__)

@sensores_bp.route("/sensores", methods=["GET"])
def get_sensores():
    return jsonify({"mensagem": "Sensores funcionando!"})
=======
from flask import Blueprint, request, jsonify
from utils.estoque import atualizar_estoque, carregar_estoque, salvar_estoque

sensores_bp = Blueprint("sensores", __name__)

# Rota para receber dados do ESP32 (peso, id do ingrediente etc.)
@sensores_bp.route("/atualizar", methods=["POST"])
def atualizar_sensores():
    dados = request.get_json()  # Recebe JSON enviado pelo ESP32

    if not dados or "id" not in dados or "peso" not in dados:
        return jsonify({"erro": "Formato inválido. Esperado: {id, peso}"}), 400

    id_ingrediente = dados["id"]
    peso = dados["peso"]

    # Carrega o estoque atual
    estoque = carregar_estoque()

    # Atualiza o peso do ingrediente
    if id_ingrediente in estoque:
        estoque[id_ingrediente]["peso"] = peso
    else:
        # Caso o ingrediente ainda não exista no estoque
        estoque[id_ingrediente] = {"peso": peso, "validade": "indefinido"}

    # Salva o estoque atualizado
    salvar_estoque(estoque)

    return jsonify({"mensagem": f"Estoque do ingrediente '{id_ingrediente}' atualizado com sucesso!"}), 200
>>>>>>> main
