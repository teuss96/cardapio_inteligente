from flask import Flask
from routes.sensores import sensores_bp
from routes.produtos import produtos_bp

app = Flask(__name__)

# Registrar as rotas
app.register_blueprint(sensores_bp)
app.register_blueprint(produtos_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
