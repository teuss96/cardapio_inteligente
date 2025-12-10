from flask import Blueprint, jsonify
from utils.preco import atualizar_preco
from utils.cozinha import carregar_cozinha
import json
import os

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/cardapio", methods=["GET"])
def get_cardapio():
    # Carrega os dados dos JSONs
    # O caminho é relativo ao diretório back_end
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pratos_path = os.path.join(base_dir, "data", "pratos.json")
    
    with open(pratos_path, "r", encoding="utf-8") as f:
        pratos = json.load(f)
    
    cozinha = carregar_cozinha()

    # Formata os pratos no formato esperado pelo front-end
    cardapio = []
    
    for nome_prato, prato in pratos.items():
        ingredientes = prato.get("ingredientes", [])
        disponivel = True

        # Verifica se todos os ingredientes estão disponíveis na cozinha
        for ingrediente_id in ingredientes:
            ingrediente_id_str = str(ingrediente_id)
            
            # Verifica se ingrediente está na cozinha
            if ingrediente_id_str not in cozinha:
                disponivel = False
                break

            item_cozinha = cozinha[ingrediente_id_str]
            
            # Verifica se está disponível (disponivel: true)
            # e se tem quantidade suficiente (peso >= pesoMin)
            if not item_cozinha.get("disponivel", False):
                disponivel = False
                break
            
            # Verifica se tem quantidade suficiente
            peso = item_cozinha.get("peso", 0)
            peso_min = item_cozinha.get("pesoMin", 0)
            if peso < peso_min:
                disponivel = False
                break

        preco = atualizar_preco(prato, cozinha, prato.get("preco_base", 0))
        
        # Formata o nome do prato (converte snake_case para título)
        nome_formatado = nome_prato.replace("_", " ").title()
        
        # Cria o objeto do prato no formato esperado pelo front-end
        prato_formatado = {
            "id": nome_prato,
            "nome": nome_formatado,
            "preco": preco,
            "categoria": "Pratos",  # Pode ser ajustado conforme necessário
            "categoria_nome": "Pratos",
            "desc": f"Delicioso {nome_formatado.lower()} preparado com ingredientes frescos.",
            "status": disponivel,
            "disponivel": disponivel,
            "imagem": "",
            "foto": "",
            "promocao": False
        }
        
        cardapio.append(prato_formatado)

    return jsonify(cardapio)


