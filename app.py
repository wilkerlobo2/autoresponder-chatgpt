from flask import Flask, request, jsonify from openai import OpenAI import os import re import requests import threading import time

app = Flask(name) client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558" WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

historico_conversas = {} mensagens_agendadas = {}

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
            if "0" in username:
                aviso += "✅ Número *0* (zero)\n"
            aviso += "Digite exatamente como enviado, respeitando maiúsculas e minúsculas."

        return msg + "\n\n⏳ *Seu teste dura 3 horas.*" + aviso
    else:
        return "❌ Erro ao gerar o login. Tente novamente em instantes."
except:
    return "⚠️ Erro ao conectar com o servidor de testes."

def agendar_mensagens(numero): def apos_30_min(): mensagens_agendadas[numero].append({"message": "Tudo certo por aí? Conseguiu usar direitinho o app? 😉"})

def apos_3_horas():
    planos = (
        "Seu teste terminou. 😔\n\nVeja nossos planos:",
        "1 mês: R$ 26\n2 meses: R$ 47\n3 meses: R$ 68\n6 meses: R$ 129\n1 ano: R$ 185\n\n"
        "💳 Aceitamos PIX ou cartão. Quer continuar? 😊"
    )
    mensagens_agendadas[numero].append({"message": planos[0]})
    mensagens_agendadas[numero].append({"message": planos[1]})

threading.Timer(1800, apos_30_min).start()   # 30 minutos
threading.Timer(10800, apos_3_horas).start() # 3 horas

@app.route("/", methods=["POST"]) def responder(): data = request.get_json() nome = data.get("name", "") numero = nome.strip() mensagem = data.get("message", "").lower() resposta = []

if numero not in historico_conversas:
    historico_conversas[numero] = []
    mensagens_agendadas[numero] = []

# Verifica se há mensagens agendadas
if mensagens_agendadas[numero]:
    resposta += mensagens_agendadas[numero]
    mensagens_agendadas[numero] = []
    return jsonify({"replies": resposta})

historico_conversas[numero].append(f"Cliente: {mensagem}")

contexto = "\n".join(historico_conversas[numero][-10:])
prompt = (
    f"Histórico recente com o cliente:\n{contexto}\n\n"
    f"Mensagem mais recente: '{mensagem}'\n\n"
    "Responda como um atendente inteligente e amigável de IPTV:\n"
    "1. Cumprimente se ainda não cumprimentou.\n"
    "2. Recomende o app certo conforme o dispositivo:\n"
    "   - Xcloud: Roku, LG, Samsung, Philco\n"
    "   - Xtream IPTV Player: Android, TV Box, Celular, Fire Stick\n"
    "   - Smarters Player Lite: iPhone/iOS ou computador\n"
    "   - OTT Player ou Duplecast (com QR): AOC/Philips\n"
    "3. Se cliente disser que instalou, gere login e avise que é para digitar o login.\n"
    "4. Após o login, explique que o teste é de 3 horas e que irá perguntar depois.\n"
    "5. Nunca diga 'colar o login'.\n"
    "6. Se teste acabar, envie os planos.\n"
    "7. Seja natural, claro e humano.\n"
    "Responda com o texto exato para WhatsApp."
)

try:
    resposta_chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    texto = resposta_chat.choices[0].message.content
    historico_conversas[numero].append(f"IA: {texto}")

    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
        if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
            login = gerar_login(WEBHOOK_XCLOUD)
        else:
            login = gerar_login(WEBHOOK_GERAL)
        resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        agendar_mensagens(numero)
    else:
        resposta.append({"message": texto})

except Exception as e:
    resposta.append({"message": f"⚠️ Erro: {str(e)}"})

return jsonify({"replies": resposta})

if name == "main": app.run(host="0.0.0.0", port=10000)

