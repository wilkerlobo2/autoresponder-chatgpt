from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
historico_conversas = {}

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip().lower()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Mensagem de boas-vindas fixa
    if numero not in historico_conversas:
        historico_conversas[numero] = []
        boas_vindas = (
            "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
        return jsonify({"replies": [{"message": boas_vindas}]})

    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    # Regra especial para PC
    if any(p in mensagem for p in ["pc", "computador", "notebook", "windows", "macbook"]):
        texto_pc = (
            "Para PC, você precisa baixar o app usando o link:\n"
            "https://7aps.online/iptvsmarters\n\n"
            "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
        )
        historico_conversas[numero].append(f"IA: {texto_pc}")
        return jsonify({"replies": [{"message": texto_pc}]})

    # Detectar confirmação de instalação
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        ultimas = [m for m in historico_conversas[numero][-6:] if m.startswith("Cliente:")]
        mensagem_relevante = " ".join(ultimas).lower()

        if "xcloud" in mensagem_relevante:
            codigo = "91"
        elif "samsung" in mensagem_relevante:
            codigo = "91"
        elif any(d in mensagem_relevante for d in ["tv box", "android", "xtream", "celular", "projetor"]):
            codigo = "555"
        elif any(d in mensagem_relevante for d in ["iphone", "ios"]):
            codigo = "224"
        elif any(d in mensagem_relevante for d in ["computador", "pc", "notebook", "macbook", "windows"]):
            codigo = "224"
        elif "philco antiga" in mensagem_relevante:
            codigo = "98"
        elif "tv antiga" in mensagem_relevante or "smart stb" in mensagem_relevante:
            codigo = "88"
        else:
            codigo = "91"

        texto = f"Digite **{codigo}** aqui na conversa para receber seu login. ☺️"
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
        return jsonify({"replies": resposta})

    # Gatilho do teste
    if mensagem.strip() in ["224", "555", "91", "88", "98"]:
        resposta.append({"message": "🔓 Gerando seu login de teste, só um instante..."})
        return jsonify({"replies": resposta})

    # Prompt para a IA
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use emojis criativos sempre que indicar um aplicativo. NÃO envie links de IPTV ou imagens.\n\n"
        "🕒 Informe sempre que o teste gratuito dura *3 horas* — e não 24 horas.\n"
        "Se o cliente perguntar sobre valores ou preços, envie os planos:\n"
        "💰 Planos disponíveis:\n"
        "1 mês – R$ 26,00\n"
        "2 meses – R$ 47,00\n"
        "3 meses – R$ 68,00\n"
        "6 meses – R$ 129,00\n"
        "1 ano – R$ 185,00\n\n"
        "💳 Formas de pagamento:\n"
        "Pix (envie o CNPJ sozinho na próxima mensagem para facilitar cópia): 46.370.366/0001-97\n"
        "Cartão: https://mpago.la/2Nsh3Fq\n\n"
        "⚠️ Envie o Pix (CNPJ) sempre separado para facilitar a cópia.\n\n"
        "Quando o cliente disser o aparelho (ex: TV LG, Roku, iPhone, Computador), diga QUAL app ele deve baixar e diga:\n"
        "'Baixe o app [NOME] 📺👇📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"
        "Se for Samsung, sempre diga que o app é o Xcloud.\n"
        "Se for LG, Roku ou Philco nova, também use o app Xcloud.\n"
        "Se for Android, TV Box, projetor ou celular Android: Xtream IPTV Player.\n"
        "Se o cliente perguntar por outros apps Android, indique também 9xtream, XCIPTV ou Vu IPTV Player.\n"
        "Se for iPhone ou iOS: diga que é o app Smarters Player Lite (da App Store, ícone azul).\n"
        "Se for computador, PC, notebook ou sistema Windows:\n"
        "1️⃣ Diga: 'Para PC, você precisa baixar o app usando o link:'\n"
        "2️⃣ Envie o link sozinho: https://7aps.online/iptvsmarters\n"
        "3️⃣ Depois diga: 'Depois me avise quando abrir o link para que eu possa enviar o seu login.'\n"
        "⚠️ NÃO diga que não precisa instalar app. O link é para *baixar o app para PC*.\n"
        "⚠️ Só diga para digitar *224* DEPOIS que o cliente disser que abriu ou instalou.\n\n"
        f"Histórico da conversa:\n{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
    )

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        texto = resposta_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})

        # Verifica se deve mandar o Pix separado
        if "pix" in mensagem or "pagamento" in mensagem or "valor" in mensagem or "quanto" in mensagem or "plano" in mensagem:
            resposta.append({"message": "Pix (CNPJ): 46.370.366/0001-97"})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
