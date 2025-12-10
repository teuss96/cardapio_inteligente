import json

# Carrega o estoque do arquivo JSON
def carregar_estoque():
    with open("data/estoque.json", "r") as f:
        return json.load(f)

# Salva o estoque no arquivo JSON
def salvar_estoque(estoque):
    with open("data/estoque.json", "w") as f:
        json.dump(estoque, f, indent=4)

# Atualiza o peso de um ingrediente
def atualizar_estoque(id_produto, peso):
    estoque = carregar_estoque()
    if id_produto in estoque:
        estoque[id_produto]["peso"] = peso
        
    salvar_estoque(estoque)
    return estoque
