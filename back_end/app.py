from flask import Flask
from flask_cors import CORS
from routes.sensores import sensores_bp
from routes.produtos import produtos_bp

app = Flask(__name__)

CORS(app)

app.register_blueprint(produtos_bp, url_prefix="/produtos")
app.register_blueprint(sensores_bp, url_prefix="/sensores")
@app.route('/')
def home():
    return "Servidor Flask funcionando! 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
