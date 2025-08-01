from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re
import requests

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

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

    contexto = "\n".join(historico_conversas[numero][-15:])
    prompt = (
        f"Você é um atendente virtual inteligente que conversa de forma humana e natural com o cliente sobre IPTV.\n"
        f"Use criatividade, educação e simpatia em todas as mensagens.\n\n"
        f"Regras importantes:\n"
        f"- Ao identificar o dispositivo (ex: TV Samsung, LG, Roku, Android, iPhone, etc), indique o app correto.\n"
        f"- Se o cliente disser que já instalou, gere o login automaticamente usando:\n"
        f"   - Xcloud → {WEBHOOK_XCLOUD}\n"
        f"   - Outros → {WEBHOOK_GERAL}\n"
        f"- Sempre diga 'digitar o login', nunca 'colar'.\n"
        f"- Informe que o teste dura 3 horas.\n"
        f"- Seja direto, mas sempre simpático.\n"
        f"- Se o cliente enviar foto ou áudio, diga que vai aguardar um atendente humano.\n\n"
        f"Exemplo de geração de login:\n"
        f"'Estou gerando seu login. Assim que estiver pronto, te envio para você digitar e começar o teste!'\n\n"
        f"Histórico:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n"
        f"Responda com o texto exato a ser enviado no WhatsApp."
    )

    try:
        if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
            if any(x in mensagem for x in ["roku", "samsung", "lg", "philco", "xcloud"]):
                login = gerar_login(WEBHOOK_XCLOUD)
            else:
                login = gerar_login(WEBHOOK_GERAL)
            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            texto = response.choices[0].message.content
            historico_conversas[numero].append(f"IA: {texto}")
            resposta.append({"message": texto})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
