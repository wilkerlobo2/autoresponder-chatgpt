from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

historico = {}

def contem_variacao_instalado(msg):
    msg = msg.lower()
    return any(palavra in msg for palavra in ["instalei", "baixei", "já instalei", "já baixei"])

def contem_caracteres_parecidos(texto):
    return any(c in texto for c in ['I', 'l', 'O', '0'])

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    numero = data.get("senderName", "")
    mensagem = data.get("message", "").lower()

    resposta = []

    if numero not in historico:
        historico[numero] = {"etapa": "inicio"}

    etapa = historico[numero]["etapa"]

    if etapa == "inicio" and "samsung" in mensagem:
        resposta.append({
            "message": "Baixe o app Xcloud 📺⬇️📲 para Samsung!\nMe avise quando instalar para que eu envie o seu login."
        })
        historico[numero]["etapa"] = "aguardando_instalacao"

    elif etapa == "aguardando_instalacao" and contem_variacao_instalado(mensagem):
        try:
            r = requests.post("https://a.opengl.in/chatbot/check/?k=66b125d558", json={"message": "91"}, timeout=10)
            if r.status_code == 200:
                login = r.text.strip()
                texto = f"🔑 Pronto! Aqui está seu login de teste:\n\n{login}"
                if contem_caracteres_parecidos(login):
                    texto += "\n\n⚠️ Atenção: verifique letras como I/l ou O/0 que podem confundir. Digite exatamente como está."
                resposta.append({"message": texto})
                historico[numero]["etapa"] = "login_enviado"
            else:
                resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente."})
        except Exception:
            resposta.append({"message": "⚠️ Erro ao gerar login. Tente novamente."})

    else:
        resposta.append({
            "message": "Olá! 👋 Me diga qual aparelho você vai usar (ex: TV Samsung, LG, Roku, Android...)?"
        })

    return jsonify({"replies": resposta})
