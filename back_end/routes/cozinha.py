from flask import Blueprint, jsonify, request
from utils.cozinha import *

cozinha_bp = Blueprint('cozinha', __name__)

@cozinha_bp.route('/', methods=['GET'])
def get_todos():
    dados = carregar_cozinha()
    return jsonify(dados)

@cozinha_bp.route('/<chave>', methods=['GET'])
def get_item(chave):
    cozinha = carregar_cozinha()
    if chave in cozinha:
        return jsonify(cozinha[chave])
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/ativo', methods=['GET'])
def get_ativo():
    chave, item = item_ativo()
    if item:
        return jsonify(item)
    return jsonify({"erro": "Nenhum produto ativo"}), 404


@cozinha_bp.route('/<chave>/disponivel', methods=['POST'])
def marcar_disponivel(chave):
    if atualizar_disponibilidade(chave, True):
        return jsonify({"mensagem": f"Produto {chave} marcado como DISPONÍVEL"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/<chave>/indisponivel', methods=['POST'])
def marcar_indisponivel(chave):
    if atualizar_disponibilidade(chave, False):
        return jsonify({"mensagem": f"Produto {chave} marcado como INDISPONÍVEL"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/<chave>/ativo', methods=['POST'])
def marcar_ativo(chave):
    if atualizar_produto_ativo(chave):
        return jsonify({"mensagem": f"Produto {chave} marcado como ATIVO"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/<chave>/peso', methods=['POST'])
def atualizar_peso_endpoint(chave):
    dados = request.get_json(force=True, silent=True) or {}
    peso = dados.get('peso')
    
    if peso is None:
        return jsonify({"erro": "Campo 'peso' é obrigatório"}), 400
    
    try:
        peso_float = float(peso)
        if peso_float < 0:
            return jsonify({"erro": "Peso não pode ser negativo"}), 400
    except (ValueError, TypeError):
        return jsonify({"erro": "Peso deve ser um número válido"}), 400
    
    if atualizar_peso(chave, peso_float):
        return jsonify({"mensagem": f"Peso do produto {chave} atualizado para {peso_float}g"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404