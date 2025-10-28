import json
from utils.preco import atualizar_preco

# Função para carregar o estoque
def carregar_estoque():
    with open("data/estoque.json", "r") as f:
        return json.load(f)

# Função para carregar os pratos
def carregar_pratos():
    with open("data/pratos.json", "r") as f:
        return json.load(f)

# Função para testar o cardápio
def testar_cardapio():
    estoque = carregar_estoque()
    pratos = carregar_pratos()

    print("📦 Estoque atual:")
    for k, v in estoque.items():
        print(f"   {k}: peso={v['peso']}, validade={v['validade']}")

    print("\n📋 Pratos disponíveis:")
    for nome, prato in pratos.items():
        ingredientes = prato["ingredientes"]
        disponivel = True
        print(f"\n🍽️ {nome} (preço base: {prato['preco_base']})")
        
        for ingrediente in ingredientes:
            item_estoque = estoque.get(ingrediente, {"peso": 0, "validade": "N/A"})
            peso = float(item_estoque.get("peso", 0))
            validade = item_estoque.get("validade", "N/A")
            print(f"   🔹 {ingrediente}: peso={peso}, validade={validade}")
            
            if peso <= 0:
                disponivel = False
                print(f"   ❌ Ingrediente insuficiente: {ingrediente}")
                break  # sai do loop, prato não disponível
        
        preco = atualizar_preco(prato, estoque, prato["preco_base"])
        print(f"   💰 Preço atualizado: {preco}")
        print(f"   ✅ Disponível: {disponivel}")

if __name__ == "__main__":
    testar_cardapio()
