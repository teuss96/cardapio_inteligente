from flask import Flask, jsonify
from flask_cors import CORS
from routes.cozinha import cozinha_bp
from routes.produtos import produtos_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(cozinha_bp, url_prefix='/cozinha')
app.register_blueprint(produtos_bp, url_prefix='/produtos')

@app.route('/')
def home():
    return jsonify({
        "mensagem": "Sistema da Cozinha",
        "status": "online",
        "endpoints": {
            "ver_todos": "GET /cozinha",
            "ver_item": "GET /cozinha/1",
            "atualizar_ativo": "POST /cozinha/1/ativo",
            "marcar_disponivel": "POST /cozinha/1/disponivel",
            "marcar_indisponivel": "POST /cozinha/1/indisponivel",
            "ver_ativo": "GET /cozinha/ativo",
            "cardapio": "GET /produtos/cardapio"
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor da Cozinha")
    print("=" * 50)
    print("Rodando em: http://localhost:5000")
    print("Endpoints:")
    print("  GET  /cozinha")
    print("  GET  /cozinha/ativo")
    print("  GET  /cozinha/1")
    print("  POST /cozinha/1/ativo")
    print("  POST /cozinha/1/disponivel")
    print("  POST /cozinha/1/indisponivel")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
