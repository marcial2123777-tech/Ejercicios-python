from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os
import random

load_dotenv()

app = Flask(__name__)

# ==============================
# CONEXIÓN A MONGODB ATLAS
# ==============================

MONGO_URI = os.getenv("MONGO_URI")

cliente = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = cliente["ejercicios_python"]
coleccion_adivina = db["adivina_numero"]

try:
    cliente.admin.command("ping")
    print("✅ CONECTADO A MONGODB ATLAS")
except Exception as e:
    print("❌ ERROR DE MONGODB:", e)


# ==============================
# VARIABLES DEL JUEGO
# ==============================

numero_oculto = random.randint(1, 100)
intentos = 0


# ==============================
# PÁGINA PRINCIPAL
# ==============================

@app.route("/")
def inicio():

    return render_template(
        "index.html",
        intentos=intentos,
        mensaje=None,
        ganado=False
    )


# ==============================
# ADIVINAR NÚMERO
# ==============================

@app.route("/adivinar", methods=["POST"])
def adivinar():

    global numero_oculto
    global intentos

    numero_texto = request.form["numero"].strip()

    # Validar que sea un número
    if not numero_texto.isdigit():

        return render_template(
            "index.html",
            intentos=intentos,
            mensaje="⚠️ Escribe solamente un número.",
            ganado=False
        )

    numero = int(numero_texto)

    # Validar rango
    if numero < 1 or numero > 100:

        return render_template(
            "index.html",
            intentos=intentos,
            mensaje="⚠️ El número debe estar entre 1 y 100.",
            ganado=False
        )

    intentos += 1

    # Número menor
    if numero < numero_oculto:

        mensaje = "📈 ¡El número oculto es MAYOR!"
        ganado = False

    # Número mayor
    elif numero > numero_oculto:

        mensaje = "📉 ¡El número oculto es MENOR!"
        ganado = False

    # Número correcto
    else:

        mensaje = f"🎉 ¡Correcto! El número era {numero_oculto}."
        ganado = True

        # Guardar partida en MongoDB
        documento = {
            "numero_oculto": numero_oculto,
            "intentos": intentos,
            "resultado": "Ganó",
            "fecha": datetime.now()
        }

        try:
            coleccion_adivina.insert_one(documento)
            print("✅ Partida guardada en MongoDB")
        except Exception as e:
            print("❌ No se pudo guardar:", e)

    return render_template(
        "index.html",
        intentos=intentos,
        mensaje=mensaje,
        ganado=ganado
    )


# ==============================
# NUEVA PARTIDA
# ==============================

@app.route("/nuevo")
def nuevo():

    global numero_oculto
    global intentos

    numero_oculto = random.randint(1, 100)
    intentos = 0

    return render_template(
        "index.html",
        intentos=0,
        mensaje="🎮 ¡Nueva partida! Adivina el número.",
        ganado=False
    )


# ==============================
# EJECUTAR
# ==============================

if __name__ == "__main__":
    app.run(debug=True)