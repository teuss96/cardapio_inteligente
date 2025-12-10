from datetime import datetime

def atualizar_preco(prato, cozinha, preco_base):
    desconto = 0
    for ingrediente in prato["ingredientes"]:
        if ingrediente not in cozinha:
            continue
        validade_str = cozinha[ingrediente].get("validade", "2025-12-31")
        dias_restantes = (datetime.strptime(validade_str, "%Y-%m-%d").date() - datetime.now().date()).days
        if dias_restantes <= 2:
            desconto = 0.2
            break
    return round(preco_base * (1 - desconto), 2)
