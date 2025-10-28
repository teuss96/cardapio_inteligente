from flask import Blueprint, jsonify
from utils.estoque import carregar_estoque
from utils.preco import atualizar_preco
import json

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/estoque", methods=["GET"])
def get_estoque():
    return jsonify(carregar_estoque())

@produtos_bp.route("/cardapio", methods=["GET"])
def get_cardapio():
    with open("data/pratos.json", "r") as f:
        pratos = json.load(f)
    estoque = carregar_estoque()
    
    cardapio = {}
    for nome, prato in pratos.items():
        ingredientes = prato["ingredientes"]
        disponivel = True  # Vamos supor que o prato está disponível
        for ingrediente in ingredientes:  # Para cada ingrediente do prato
         # Busca o ingrediente no estoque. Se não existir, assume peso 0.
            item_estoque = estoque.get(ingrediente)
            # print(item_estoque)
        # Se o peso do ingrediente for 0 ou menor, o prato não pode ser feito
            print(item_estoque["peso"])
            if item_estoque["peso"] <= 0:
                disponivel = False
                
                break
         
        preco = atualizar_preco(prato, estoque, prato["preco_base"])
        cardapio[nome] = {
            "preco": preco,
            "disponivel": disponivel
        }
        print(cardapio)
    return jsonify(cardapio)


