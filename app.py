from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "AutoResponder ChatGPT Flask App is running!"

@app.route("/webhook", methods=["POST"])
def responder():
    try:
        data = request.get_json(force=True)
        print("DADOS RECEBIDOS:", data)

        return jsonify({"debug": str(data)})
    except Exception as e:
        print("ERRO:", e)
        return jsonify({"error": str(e)}), 400
