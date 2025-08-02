import os
import json
import re
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

# Mensagem fixa de boas-vindas
mensagem_boas_vindas = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

# Instruções fixas para a IA
instrucoes_ia = """
Você é um atendente de IPTV. Após a mensagem de boas-vindas (que é fixa), você assume tudo.

1. Descubra o aparelho do cliente e diga o aplicativo exato que ele deve instalar, usando emojis criativos.
2. Nunca diga para o cliente "digitar o login". Em vez disso, oriente ele a digitar os códigos (91, 555, 224, 88...).
3. Quando o cliente disser que instalou, diga: "Beleza! Agora digite *555* aqui pra que o sistema envie seu login automaticamente!" (mude o número conforme o aparelho).
4. Se o cliente tiver dificuldade para instalar o app principal, ofereça alternativas compatíveis.
5. Nunca diga que todos funcionam com o mesmo login. Só fale isso se o cliente perguntar.
6. Após 30 minutos de login enviado, mande uma mensagem perguntando se funcionou.
7. Avise sempre que o login pode conter letras parecidas como *I, l, O, 0* e que o cliente deve digitar com atenção.
8. Se o cliente disser que está usando app SmartOne, peça o MAC. Se for Duplecast, peça o QR Code.
9. Se a TV for Samsung antiga e o cliente tiver dificuldade, diga que deve usar o código *88* e siga as instruções do sistema.

Apps por dispositivo:
- TV Samsung (nova): Xcloud 📺⬇️📲 → código: 91
- TV LG: Xcloud ou Duplecast (QR) ou SmartOne (MAC) → código: 555
- Roku: Xcloud → código: 88
- Android (TV Box, Projetor, Celular): Xtream IPTV Player → código: 555 (se não conseguir, sugerir 9Xtream, XCIPTV, VU IPTV Player, IPTV Xtream Player)
- Computador ou iPhone (iOS): Smarters Player Lite (azul) → código: 224
- TV antiga (Philco, AOC, Philips etc.): Smart STB → código: 88

Sempre aja com naturalidade, clareza e sem repetir frases. Seja objetivo, como numa linha de produção, mas humano.
"""

@app.route("/", methods=["POST"])
def index():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("from", "")
    mensagem = query.get("message", "")

    if not mensagem:
        return jsonify({"replies": [{"message": "Desculpe, não entendi a mensagem."}]}), 200

    # Se for a primeira interação, manda a mensagem fixa
    if "tv" in mensagem.lower() or "olá" in mensagem.lower() or "oi" in mensagem.lower():
        return jsonify({"replies": [{"message": mensagem_boas_vindas}]}), 200

    # Geração da resposta com nova API (GPT-4)
    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": instrucoes_ia},
                {"role": "user", "content": mensagem}
            ]
        )
        texto_resposta = resposta.choices[0].message.content.strip()
    except Exception as e:
        texto_resposta = "Erro ao gerar resposta com a IA."

    return jsonify({"replies": [{"message": texto_resposta}]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
