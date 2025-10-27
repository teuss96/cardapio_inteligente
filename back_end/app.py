from flask import Flask
<<<<<<< HEAD
=======
from flask_cors import CORS
>>>>>>> main
from routes.sensores import sensores_bp
from routes.produtos import produtos_bp

app = Flask(__name__)

<<<<<<< HEAD
# Registrar as rotas
app.register_blueprint(sensores_bp)
app.register_blueprint(produtos_bp)
=======
CORS(app)

app.register_blueprint(produtos_bp, url_prefix="/produtos")
app.register_blueprint(sensores_bp, url_prefix="/sensores")
@app.route('/')
def home():
    return "Servidor Flask funcionando! 🚀"

>>>>>>> main

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
