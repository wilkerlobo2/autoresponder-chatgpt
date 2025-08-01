from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

historico_conversas = {}

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    nome = data.get("name", "")
    numero = nome.strip()
    mensagem = data.get("message", "").strip()
    resposta = []

    if numero not in historico_conversas:
        historico_conversas[numero] = []

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    prompt = (
        f"Você está conversando com um cliente pelo WhatsApp. Seja educado, natural, simpático e criativo.\n"
        f"Converse como um atendente humano real.\n"
        f"Histórico da conversa:\n{contexto}\n\n"
        f"Mensagem do cliente: '{mensagem}'\n\n"
        f"Responda da forma mais natural e útil possível para o WhatsApp."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        texto = response.choices[0].message.content
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


Pronto! O código app.py agora está completamente limpo, sem regras fixas. A IA vai conversar de forma natural com o cliente no WhatsApp, como estamos conversando aqui.

Pode fazer o teste no seu número. Se quiser, depois adicionamos de volta a lógica de login, testes, apps etc. conforme você desejar.

