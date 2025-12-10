import json
import os

def _get_data_path(filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", filename)

def carregar_cozinha():
    cozinha_path = _get_data_path("cozinha.json")
    with open(cozinha_path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_cozinha(dados):
    cozinha_path = _get_data_path("cozinha.json")
    with open(cozinha_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def buscar_item(nome):
    cozinha = carregar_cozinha()
    for key, produto in cozinha.items():
        if produto.get('nome') == nome:
            return produto
    return None

def buscar_item_por_id(id_procurado):
  
    cozinha = carregar_cozinha()
    if str(id_procurado) in cozinha:
        return cozinha[str(id_procurado)]
    
    for key, produto in cozinha.items():
        if str(produto.get('id')) == str(id_procurado):
            return produto
    return None

def buscar_chave_por_id(id_procurado):
    cozinha = carregar_cozinha()
    if str(id_procurado) in cozinha:
        return str(id_procurado)
    
    for key, produto in cozinha.items():
        if str(produto.get('id')) == str(id_procurado):
            return key
    return None

def item_ativo():
    cozinha = carregar_cozinha()
    for chave, produto in cozinha.items():
        if produto.get('ativo') == True:
            return chave, produto  
    return None, None  

def atualizar_peso(chave, novo_peso):
    cozinha = carregar_cozinha()
    if chave in cozinha:
        cozinha[chave]["peso"] = novo_peso
        salvar_cozinha(cozinha)
        return True
    return False

def atualizar_peso_por_id(id_procurado, novo_peso):
    chave = buscar_chave_por_id(id_procurado)
    if chave:
        return atualizar_peso(chave, novo_peso)
    return False

def atualizar_disponibilidade(chave, disponivel):
    cozinha = carregar_cozinha()
    if chave in cozinha:
        cozinha[chave]["disponivel"] = disponivel
        salvar_cozinha(cozinha)
        return True
    return False

def atualizar_disponibilidade_por_id(id_procurado, disponivel):
    chave = buscar_chave_por_id(id_procurado)
    if chave:
        return atualizar_disponibilidade(chave, disponivel)
    return False

def atualizar_produto_ativo(id_procurado):
    cozinha = carregar_cozinha()
    chave = buscar_chave_por_id(id_procurado)
    
    if chave:
        for produto_chave in cozinha:
            cozinha[produto_chave]["ativo"] = False
        
        cozinha[chave]["ativo"] = True
        salvar_cozinha(cozinha)
        return True
    return False