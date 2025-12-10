from flask import Blueprint, jsonify
from utils.preco import atualizar_preco
from utils.cozinha import carregar_cozinha
import json

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/cardapio", methods=["GET"])
def get_cardapio():
    with open("data/pratos.json", "r") as f:
        pratos = json.load(f)
    cozinha = carregar_cozinha()

    cardapio = {}
    for nome, prato in pratos.items():
        ingredientes = prato["ingredientes"]
        disponivel = True

        for ingrediente in ingredientes:
            # Verifica se ingrediente está na cozinha
            if ingrediente not in cozinha:
                print("error 1")
                disponivel = False
                break

            item_cozinha = cozinha[ingrediente]
            
            # Verifica se está ativo
            if not item_cozinha.get("disponivel", False):
                print("error 2")
                disponivel = False
                break

        preco = atualizar_preco(prato, cozinha, prato["preco_base"])
        
        cardapio[nome] = {
            "preco": preco,
            "disponivel": disponivel
        }

    return jsonify(cardapio)


