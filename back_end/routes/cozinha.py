from flask import Blueprint, jsonify, request
from utils.cozinha import *

cozinha_bp = Blueprint('cozinha', __name__)

@cozinha_bp.route('/', methods=['GET'])
def get_todos():
    """GET /cozinha - Retorna todos os ingredientes"""
    dados = carregar_cozinha()
    return jsonify(dados)

@cozinha_bp.route('/<chave>', methods=['GET'])
def get_item(chave):
    """GET /cozinha/1 - Retorna por CHAVE (ex: '1', '2', '3')"""
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
    """POST /cozinha/1/disponivel"""
    if atualizar_disponibilidade(chave, True):
        return jsonify({"mensagem": f"Produto {chave} marcado como DISPONÍVEL"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/<chave>/indisponivel', methods=['POST'])
def marcar_indisponivel(chave):
    """POST /cozinha/1/indisponivel"""
    if atualizar_disponibilidade(chave, False):
        return jsonify({"mensagem": f"Produto {chave} marcado como INDISPONÍVEL"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404

@cozinha_bp.route('/<chave>/ativo', methods=['POST'])
def marcar_ativo(chave):
    """POST /cozinha/1/ativo - Ativa produto"""
    if atualizar_produto_ativo(chave):
        return jsonify({"mensagem": f"Produto {chave} marcado como ATIVO"})
    return jsonify({"erro": f"Chave '{chave}' não encontrada"}), 404