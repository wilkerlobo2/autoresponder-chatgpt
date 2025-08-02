import os
from flask import Flask, request, jsonify
from datetime import datetime
import openai

app = Flask(__name__)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

historico_conversas = {}

mensagem_boas_vindas = (
    "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
    "Vamos começar seu teste gratuito?\n\n"
    "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
)

instrucoes_ia = """
Você é um atendente de IPTV prestativo e direto. Seu objetivo é conduzir o cliente do início ao fim do atendimento, sempre de forma simples, curta e objetiva, como uma linha de produção.

📌 Regras e conhecimento:

1. A mensagem de boas-vindas já foi enviada automaticamente. Não repita.
2. Espere o cliente dizer o aparelho/dispositivo para indicar o app correto.
3. Sempre diga diretamente qual app deve ser usado, com emojis e instruções como:
   - “Baixe o app Xcloud 📺⬇️📲 para Samsung! Me avise quando instalar para que eu envie o seu login.”
4. Após o cliente dizer “instalei”, “baixei” ou similar, oriente ele a digitar o número correspondente:
   - Samsung (Xcloud): digitar `91`
   - Android, Android TV, TV Box, Projetor, Celular Android: `555`
   - Computador, iPhone (iOS): `224`
   - Roku antiga, Philco antiga, TV antiga, etc: `88`
5. Para Android, indique o app *Xtream IPTV Player*. Se o cliente não conseguir instalar, ofereça:
   - 9Xtream Player, XCIPTV Player, VU IPTV Player, IPTV Xtream Player.
   - Todos usam o mesmo login (555), mas **não diga isso ao cliente diretamente**.
6. Se o cliente perguntar se há outras opções, diga que sim, e cite as alternativas.
7. Após o cliente digitar o número, o outro app (AutoReply) cuida do envio do login.
8. Após 30 minutos do envio do número, pergunte se está funcionando.
9. Após 3 horas, diga que o teste acabou e envie os planos de forma criativa:
   - R$ 26 (1 mês), R$ 47 (2 meses), R$ 68 (3 meses), R$ 129 (6 meses), R$ 185 (1 ano).
10. Se o login contiver letras como “I”, “l”, “O”, “0”, alerte o cliente sobre possíveis confusões.
11. Nunca envie o login diretamente. Apenas oriente a digitar o número (ex: 91).
12. Caso o cliente diga que já tem o app instalado (ex: “já tenho o SmartOne”), antecipe e peça o MAC.
13. Em casos de dúvida ou perguntas sobre IPTV, DNS, instalação, letras maiúsculas e minúsculas, etc., responda com naturalidade e clareza.
14. Seja educado, use emojis de forma criativa e evite repetições.
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    query = data.get("query", {})
    sender = query.get("from")
    mensagem = query.get("message", "").strip()

    if not sender or not mensagem:
        return jsonify({"replies": [{"message": "Mensagem inválida recebida."}]}), 400

    historico = historico_conversas.get(sender, [])

    # Primeira mensagem da conversa → envia a mensagem fixa de boas-vindas
    if not historico:
        historico_conversas[sender] = [
            {"role": "system", "content": instrucoes_ia},
            {"role": "user", "content": mensagem}
        ]
        return jsonify({"replies": [{"message": mensagem_boas_vindas}]})

    # Adiciona mensagem do usuário ao histórico
    historico.append({"role": "user", "content": mensagem})

    # Geração da resposta com nova API
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=historico,
        temperature=0.7,
    )
    texto_resposta = resposta.choices[0].message.content.strip()

    # Adiciona resposta da IA ao histórico
    historico.append({"role": "assistant", "content": texto_resposta})
    historico_conversas[sender] = historico

    return jsonify({"replies": [{"message": texto_resposta}]})

@app.route("/autoreply", methods=["POST"])
def autoreply():
    data = request.get_json()
    mensagem = data.get("query", {}).get("message", "").strip()

    respostas = {
        "91": "Login enviado! 📺 Aproveite sua programação! Qualquer dúvida, me chama aqui! 😉",
        "555": "Login enviado! ✅ Abra o app e digite o login manualmente. Qualquer dúvida, estou por aqui! 🤖",
        "224": "Login ativado! 🖥️ Teste à vontade no seu computador ou iPhone! Me avise se tiver dúvidas. 👍",
        "88": (
            "🧠 Seu login de teste foi gerado!\n\n"
            "📽️ Assista o vídeo com o passo a passo: https://youtu.be/7IAnxvLnntE\n"
            "🌐 Use o DNS: 1.1.1.1 ou 8.8.8.8\n"
            "🔁 Desligue e ligue a TV após instalar o app.\n"
            "📲 App: *SMART STB*\n\n"
            "👤 Usuário: [LOGIN]\n🔑 Senha: [SENHA]\n💰 Mensalidade: R$ 26,00\n\n"
            "✅ Se funcionar, digite *100* aqui pra assinar!"
        ),
    }

    resposta = respostas.get(mensagem, "Código inválido. Verifique e tente novamente. 😉")

    return jsonify({"replies": [{"message": resposta}]})

if __name__ == "__main__":
    app.run(debug=True)
