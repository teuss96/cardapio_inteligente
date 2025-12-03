from flask import Flask
from flask_cors import CORS
import os

# Importa blueprints
try:
    from routes.sensores import sensores_bp
    from routes.produtos import produtos_bp
    BLUEPRINTS_LOADED = True
except ImportError as e:
    print(f"⚠️ Aviso: Não foi possível carregar blueprints: {e}")
    BLUEPRINTS_LOADED = False

app = Flask(__name__)
CORS(app)  # Permite CORS para todas as rotas

# Registra blueprints apenas se carregados
if BLUEPRINTS_LOADED:
    app.register_blueprint(produtos_bp, url_prefix="/produtos")
    app.register_blueprint(sensores_bp, url_prefix="/sensores")
    print("✅ Blueprints registrados com sucesso")
else:
    print("⚠️ Servidor rodando sem blueprints")

@app.route('/')
def home():
    return {
        "status": "online",
        "message": "Servidor Flask para ESP32",
        "endpoints": {
            "sensores": "/sensores/dados",
            "produtos": "/produtos/",
            "health": "/health"
        }
    }

@app.route('/health')
def health_check():
    """Endpoint para health check do Render"""
    return {"status": "healthy"}, 200

@app.route('/test')
def test():
    """Endpoint de teste simples"""
    return {"message": "API funcionando!", "timestamp": "2024-01-01T00:00:00Z"}

# Para desenvolvimento local
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host="0.0.0.0", port=port, debug=debug)