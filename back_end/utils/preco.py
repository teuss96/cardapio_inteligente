from datetime import datetime

# Calcula o preço do prato aplicando desconto se algum ingrediente estiver perto da validade
def atualizar_preco(prato, estoque, preco_base):
    desconto = 0

    for ingrediente in prato["ingredientes"]:
        if ingrediente not in estoque:
            continue
        validade_str = estoque[ingrediente].get("validade", "2025-12-31")
        dias_restantes = (datetime.strptime(validade_str, "%Y-%m-%d").date() - datetime.now().date()).days
        if dias_restantes <= 2:
            desconto = 0.2  # aplica desconto de 20%
            break

    return round(preco_base * (1 - desconto), 2)
