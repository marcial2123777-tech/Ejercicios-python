from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# ==========================================
# CONFIGURACIÓN
# ==========================================

load_dotenv()

app = Flask(__name__)


# ==========================================
# CONEXIÓN MONGODB
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")

cliente = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = cliente["ejercicios_python"]

# Colección exclusiva para este proyecto
coleccion_multiplicacion = db["multiplicacion"]


# ==========================================
# COMPROBAR CONEXIÓN
# ==========================================

try:
    cliente.admin.command("ping")
    print("✅ CONECTADO A MONGODB ATLAS")

except Exception as e:
    print("❌ ERROR DE MONGODB:", e)


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    return render_template(
        "index.html",
        tabla=None
    )


# ==========================================
# GENERAR TABLA
# ==========================================

@app.route("/multiplicar", methods=["POST"])
def multiplicar():

    numero_texto = request.form["numero"].strip()

    # Comprobar que sean números
    if not numero_texto.isdigit():
        return "Error: solo se permiten números", 400

    # Máximo 15 dígitos
    if len(numero_texto) > 15:
        return "Error: máximo 15 dígitos", 400

    numero = int(numero_texto)

    # Generar resultados
    tabla = []

    for i in range(1, 11):

        tabla.append({
            "multiplicador": i,
            "resultado": numero * i
        })

    # Guardar en MongoDB
    documento = {
        "numero": numero,
        "tabla": tabla,
        "fecha": datetime.now()
    }

    coleccion_multiplicacion.insert_one(documento)

    return render_template(
        "index.html",
        tabla=tabla,
        numero=numero
    )


# ==========================================
# EJECUTAR
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)