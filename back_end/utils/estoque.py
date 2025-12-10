import json
import os

def _get_data_path(filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", filename)

def carregar_estoque():
    estoque_path = _get_data_path("estoque.json")
    with open(estoque_path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_estoque(estoque):
    estoque_path = _get_data_path("estoque.json")
    with open(estoque_path, "w", encoding="utf-8") as f:
        json.dump(estoque, f, indent=4)

def atualizar_estoque(id_produto, peso):
    estoque = carregar_estoque()
    if id_produto in estoque:
        estoque[id_produto]["peso"] = peso
        
    salvar_estoque(estoque)
    return estoque
