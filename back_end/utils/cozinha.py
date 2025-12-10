import json

def carregar_cozinha():
    with open("data/cozinha.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_cozinha(dados):
    with open("data/cozinha.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def buscar_item(nome):
    """Busca por NOME do produto"""
    cozinha = carregar_cozinha()
    for key, produto in cozinha.items():
        if produto.get('nome') == nome:
            return produto
    return None

def buscar_item_por_id(id_procurado):
  
    cozinha = carregar_cozinha()
    # Tenta encontrar pela chave (string)
    if str(id_procurado) in cozinha:
        return cozinha[str(id_procurado)]
    
    # Se não encontrar, procura pelo campo 'id' dentro do objeto
    for key, produto in cozinha.items():
        if str(produto.get('id')) == str(id_procurado):
            return produto
    return None

def buscar_chave_por_id(id_procurado):
    """Retorna a chave (ex: '1', '2') pelo ID"""
    cozinha = carregar_cozinha()
    # Verifica se a chave existe
    if str(id_procurado) in cozinha:
        return str(id_procurado)
    
    # Procura pelo campo 'id' dentro
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
    """Atualiza peso usando a CHAVE do JSON ('1', '2', etc)"""
    cozinha = carregar_cozinha()
    if chave in cozinha:
        cozinha[chave]["peso"] = novo_peso
        salvar_cozinha(cozinha)
        return True
    return False

def atualizar_peso_por_id(id_procurado, novo_peso):
    """Atualiza peso usando ID"""
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
    """Atualiza disponibilidade usando ID"""
    chave = buscar_chave_por_id(id_procurado)
    if chave:
        return atualizar_disponibilidade(chave, disponivel)
    return False

def atualizar_produto_ativo(id_procurado):
    """Ativa um produto pelo ID, desativa os outros"""
    cozinha = carregar_cozinha()
    chave = buscar_chave_por_id(id_procurado)
    
    if chave:
        # Primeiro, desativa todos os produtos
        for produto_chave in cozinha:
            cozinha[produto_chave]["ativo"] = False
        
        # Depois, ativa apenas o produto especificado
        cozinha[chave]["ativo"] = True
        salvar_cozinha(cozinha)
        return True
    return False