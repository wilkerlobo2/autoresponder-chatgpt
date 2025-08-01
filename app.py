from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re
import requests

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

# Memória de conversas por número
historico_conversas = {}
status_conversa = {}  # novo controle do estado do atendimento

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
        status_conversa[numero] = {
            "cumprimentado": False,
            "app_recomendado": False,
            "login_enviado": False
        }

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    estado = status_conversa[numero]

    contexto = "\n".join(historico_conversas[numero][-10:])

    prompt = (
        f"Histórico recente com o cliente:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Você é um atendente de IPTV que entende o cliente e responde com naturalidade e criatividade. Siga as regras:\n\n"
        "1. Cumprimente apenas se ainda não cumprimentou.\n"
        "2. Se o cliente disser o nome do dispositivo, recomende o app correto:\n"
        "   - Roku, LG, Samsung, Philco: Xcloud\n"
        "   - Android, TV Box, Celular, Fire Stick: Xtream IPTV Player\n"
        "   - iPhone/iOS ou computador: Smarters Player Lite\n"
        "   - AOC/Philips: OTT Player ou Duplecast (peça QR code)\n"
        "3. Se o cliente disser que já instalou (ex: 'instalei', 'baixei'), diga que está gerando o login e envie.\n"
        "4. Nunca diga 'colar o login'. Use 'digitar o login'.\n"
        "5. Após o login, oriente e diga que o teste dura 3 horas.\n"
        "6. Se o teste terminar, envie os planos:\n"
        "   - R$26 (1 mês), R$47 (2 meses), R$68 (3 meses), R$129 (6 meses), R$185 (1 ano)\n"
        "7. Explique o que é IPTV se perguntarem.\n"
        "8. Se o cliente enviar algo que não entenda (ex: foto, áudio), diga que vai aguardar um atendente humano.\n\n"
        "Responda com o texto exato que deve ser enviado no WhatsApp."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        texto = response.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")

        # Cumprimentar só se ainda não cumprimentou
        if not estado["cumprimentado"]:
            estado["cumprimentado"] = True

        # Enviar login se cliente disser que instalou
        if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]) and not estado["login_enviado"]:
            estado["login_enviado"] = True

            if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
                login = gerar_login(WEBHOOK_XCLOUD)
            else:
                login = gerar_login(WEBHOOK_GERAL)

            resposta.append({"message": f"{texto}\n\nAqui está seu login de teste:\n\n{login}"})
            resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        else:
            resposta.append({"message": texto})

    except Exception as e:
        resposta.append({"message": f"⚠️ Ocorreu um erro: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
