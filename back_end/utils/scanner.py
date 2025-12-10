# enviar_produto.py
import requests

API_URL = "http://172.26.65.26:5000"

print("=== MUDAR PRODUTO ATIVO ===")

while True:
    produto = input("\nDigite produto ou 'sair': ").strip().lower()
    
    if produto == 'sair':
        break
    
    
    try:
        # Envia POST
        url = f"{API_URL}/cozinha/{produto}/ativo"
        response = requests.post(url, json={})
        
        print(f"✅ POST: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Produto alterado com sucesso!")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
   

print("\nPrograma encerrado.")