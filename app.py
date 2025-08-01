from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re
import requests

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Armazenamento temporário de conversas
historico_conversas = {}

def gerar_login(webhook):
    try:
        r = requests.get(webhook, timeout=10)
        if r.status_code == 200:
            data = r.json()
            username = data.get("username", "")
            password = data.get("password", "")
            dns = data.get("dns", "")
            msg = f"*Usuário:* `{username}`\n*Senha:* `{password}`"
            if dns:
                msg += f"\n*DNS:* `{dns}`"

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

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    nome = data.get("name", "")
    numero = nome.strip()
    mensagem = data.get("message", "").lower()
    resposta = []

    if numero not in historico_conversas:
        historico_conversas[numero] = []

    historico_conversas[numero].append(f"Cliente: {mensagem}")

    # Montar prompt com contexto
    contexto = "\n".join(historico_conversas[numero][-10:])

    prompt = (
        f"Histórico recente com o cliente:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Responda como um atendente inteligente e criativo de IPTV. Siga as regras abaixo:\n\n"
        "1. Cumprimente de forma natural se ainda não cumprimentou.\n"
        "2. Se o cliente mencionar o dispositivo (Roku, LG, Samsung, Android, iPhone, PC, etc), recomende o app certo:\n"
        "   - Roku, LG, Samsung, Philco: *Xcloud*\n"
        "   - Android, TV Box, Celular, Fire Stick: *Xtream IPTV Player*\n"
        "   - iPhone/iOS ou computador: *Smarters Player Lite*\n"
        "   - AOC/Philips: *OTT Player* ou *Duplecast* (peça o QR code)\n"
        "3. Se o cliente disser que já instalou o app (ex: 'instalei', 'baixei', 'pronto'), responda que está gerando o login.\n"
        f"   - Use o webhook {WEBHOOK_XCLOUD} para Xcloud\n"
        f"   - Use o webhook {WEBHOOK_GERAL} para os demais\n"
        "4. Nunca diga 'colar o login', diga 'digitar o login'.\n"
        "5. Após o envio do login, oriente com clareza. Avise que o teste dura 3 horas.\n"
        "6. Se o teste terminar, envie os planos:\n"
        "   - R$ 26 (1 mês), R$ 47 (2 meses), R$ 68 (3 meses), R$ 129 (6 meses), R$ 185 (1 ano)\n"
        "7. Seja criativo, natural e amigável.\n"
        "8. Se o cliente perguntar o que é IPTV, explique de forma simples.\n"
        "9. Se o cliente enviar foto, áudio ou algo que não entenda, diga que vai aguardar um atendente humano.\n\n"
        "Responda com o texto exato a ser enviado no WhatsApp."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        texto = response.choices[0].message.content
        historico_conversas[numero].append(f"IA: {texto}")

        # Se cliente disse que já instalou, gerar login
        if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
            if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
                login = gerar_login(WEBHOOK_XCLOUD)
            else:
                login = gerar_login(WEBHOOK_GERAL)

            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
            resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        else:
            resposta.append({"message": texto})

    except Exception as e:
        resposta.append({"message": f"⚠️ Ocorreu um erro ao gerar a resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
