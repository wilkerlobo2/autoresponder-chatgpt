from flask import Flask, request, jsonify
from openai import OpenAI
import os
import threading
import time

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
historico_conversas = {}
agendados = {}

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip().lower()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Boas-vindas fixas
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

    # Se o cliente disser que já instalou o app
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei"]):
        historico = " ".join(historico_conversas[numero]).lower()
        if "samsung" in historico:
            codigo = "91"
        elif any(d in historico for d in ["tv box", "android", "xtream", "celular", "projetor"]):
            codigo = "555"
        elif any(d in historico for d in ["iphone", "ios"]):
            codigo = "224"
        elif any(d in historico for d in ["computador", "pc", "notebook", "macbook"]):
            codigo = "224"
        elif "philco antiga" in historico:
            codigo = "98"
        elif "tv antiga" in historico or "smart stb" in historico:
            codigo = "88"
        else:
            codigo = "91"  # padrão

        texto = f"Digite **{codigo}** aqui na conversa para receber seu login. 😉"
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})

        # Agendar mensagem de 30 minutos (1.800 segundos)
        if numero not in agendados:
            agendados[numero] = True
            threading.Thread(target=mensagem_agendada, args=(numero,), daemon=True).start()

        return jsonify({"replies": resposta})

    # Prompt da IA com todas as instruções
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use emojis criativos sempre que indicar um aplicativo. NÃO envie links ou imagens.\n\n"

        "Quando o cliente disser o aparelho (ex: TV LG, Roku, iPhone), diga QUAL app ele deve baixar e diga:\n"
        "'Baixe o app [NOME] 📺⬇️📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"

        "Se for Samsung, sempre diga que o app é o Xcloud.\n"
        "Se for LG, Roku ou Philco nova, também use o app Xcloud.\n"
        "Se for Android, TV Box, projetor ou celular Android: Xtream IPTV Player.\n"
        "Se o cliente pedir outros apps para Android/TV Box/projetor, mencione: 9xtream, XCIPTV, Vu IPTV Player.\n"
        "Mas só ofereça essas alternativas se o cliente tiver dificuldade com o Xtream IPTV Player.\n"
        "Se for iPhone ou iOS: o app é Smarters Player Lite.\n"
        "Se for computador: peça para abrir o navegador e acessar:\n"
        "https://7aps.online/iptvsmarters\n"
        "Depois que ele disser que baixou, peça para digitar 224.\n"
        "Se for LG antiga e o Xcloud não funcionar, indique Duplecast ou SmartOne.\n"
        "Se for Philips ou AOC: indique OTT Player ou Duplecast.\n"
        "Se for Philco antiga, use o código especial 98.\n"

        "Sempre responda dúvidas sobre IPTV, login, DNS, letras maiúsculas e minúsculas.\n"

        "Atenção: os testes duram 3 horas. Após esse tempo, ou se o cliente perguntar, envie os planos:\n"
        "💰 *PLANOS:*\n"
        "• R$ 26,00 – 1 mês\n"
        "• R$ 47,00 – 2 meses\n"
        "• R$ 68,00 – 3 meses\n"
        "• R$ 129,00 – 6 meses\n"
        "• R$ 185,00 – 1 ano\n\n"
        "*PIX (CNPJ)* para pagamento:\n"
        "`12.345.678/0001-99`\n\n"
        "Ou pergunte se o cliente quer pagar por cartão de crédito/débito. 😃\n\n"

        f"Histórico da conversa:\n{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
    )

    try:
        resposta_ia = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        texto = resposta_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

# Mensagem programada após 30 minutos
def mensagem_agendada(numero):
    time.sleep(1800)
    mensagem = (
        "⏱️ Já se passaram 30 minutos desde que você recebeu o teste.\n"
        "Conseguiu assistir direitinho? Teve algum problema? Estou aqui caso precise de ajuda! 💬"
    )
    historico_conversas[numero].append(f"IA: {mensagem}")
    agendados.pop(numero, None)
    # Aqui você pode integrar com envio externo se quiser

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
