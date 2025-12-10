from flask import Blueprint, jsonify
from utils.preco import atualizar_preco
from utils.cozinha import carregar_cozinha
import json
import os

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/cardapio", methods=["GET"])
def get_cardapio():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pratos_path = os.path.join(base_dir, "data", "pratos.json")
    
    with open(pratos_path, "r", encoding="utf-8") as f:
        pratos = json.load(f)
    
    cozinha = carregar_cozinha()

    cardapio = []
    
    for nome_prato, prato in pratos.items():
        ingredientes = prato.get("ingredientes", [])
        disponivel = True

        for ingrediente_id in ingredientes:
            ingrediente_id_str = str(ingrediente_id)
            
            if ingrediente_id_str not in cozinha:
                disponivel = False
                break

            item_cozinha = cozinha[ingrediente_id_str]
            
            if not item_cozinha.get("disponivel", False):
                disponivel = False
                break
            
            peso = item_cozinha.get("peso", 0)
            peso_min = item_cozinha.get("pesoMin", 0)
            if peso < peso_min:
                disponivel = False
                break

        preco = atualizar_preco(prato, cozinha, prato.get("preco_base", 0))
        
        nome_formatado = nome_prato.replace("_", " ").title()
        
        prato_formatado = {
            "id": nome_prato,
            "nome": nome_formatado,
            "preco": preco,
            "categoria": "Pratos",
            "categoria_nome": "Pratos",
            "desc": f"Deliciosa {nome_formatado.lower()} preparada com ingredientes frescos.",
            "status": disponivel,
            "disponivel": disponivel,
            "imagem": "",
            "foto": "",
            "promocao": False
        }
        
        cardapio.append(prato_formatado)

    return jsonify(cardapio)


