from flask import Flask, request, jsonify from openai import OpenAI import os import re import requests

app = Flask(name) client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558" WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

Armazenamento temporário de conversas

historico_conversas = {}

def gerar_login(webhook): try: r = requests.get(webhook, timeout=10) if r.status_code == 200: data = r.json() username = data.get("username", "") password = data.get("password", "") dns = data.get("dns", "") msg = f"Usuário: {username}\nSenha: {password}" if dns: msg += f"\nDNS: {dns}"

aviso = ""
        if re.search(r"[IlO0]", username):
            aviso += "\n\n⚠️ *Atenção com o login:*\n"
            if "I" in username:
                aviso += "✅ Letra *I* de *Índia*\n"
            if "l" in username:
                aviso += "✅ Letra *l* minúscula de *lápis*\n"
            if "O" in username:
                aviso += "✅ Letra *O* de *Ovo*\n"
            if "0"

