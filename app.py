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

    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        historico = " ".join(historico_conversas[numero]).lower()
        if "samsung" in historico:
            codigo = "91"
        elif any(d in historico for d in ["tv box", "android", "xtream", "celular", "projetor"]):
            codigo = "555"
        elif any(d in historico for d in ["iphone", "ios"]):
            codigo = "224"
        elif any(d in historico for d in ["computador", "pc", "notebook", "macbook", "windows"]):
            codigo = "224"
        elif "philco antiga" in historico:
            codigo = "98"
        elif "tv antiga" in historico or "smart stb" in historico:
            codigo = "88"
        else:
            codigo = "91"

        texto = f"Digite **{codigo}** aqui na conversa para receber seu login. 😉"
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
        return jsonify({"replies": resposta})

    if mensagem.strip() == "224":
        resposta.append({"message": "🔓 Gerando seu login de teste, só um instante..."})
        threading.Thread(target=agendar_mensagens, args=(numero,), daemon=True).start()
        time.sleep(4)
        resposta.append({"message": "⏱️ Seu teste dura *3 horas* para você conhecer os canais e a qualidade. Aproveite!"})
        return jsonify({"replies": resposta})

    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use emojis criativos sempre que indicar um aplicativo. NÃO envie links de IPTV ou imagens.\n\n"
        "Quando o cliente disser o aparelho (ex: TV LG, Roku, iPhone, Computador), diga QUAL app ele deve baixar e diga:\n"
        "'Baixe o app [NOME] 📺⬇️📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"
        "Se for Samsung, sempre diga que o app é o Xcloud.\n"
        "Se for LG, Roku ou Philco nova, também use o app Xcloud.\n"
        "Se for Android, TV Box, projetor ou celular Android: Xtream IPTV Player.\n"
        "Se o cliente perguntar por outros apps Android, indique também 9xtream, XCIPTV ou Vu IPTV Player.\n"
        "Se for iPhone ou iOS: diga que é o app Smarters Player Lite (ícone azul, da App Store).\n"
        "Se for computador, PC, notebook ou sistema Windows:\n"
        "1️⃣ Diga: 'Para PC, você precisa baixar o app usando o link:'\n"
        "2️⃣ Envie o link sozinho: https://7aps.online/iptvsmarters\n"
        "3️⃣ Depois diga: 'Depois me avise quando abrir o link para que eu possa enviar o seu login.'\n"
        "⚠️ Não diga que não precisa instalar app. O link é para *baixar o app para PC*.\n"
        "⚠️ Só diga para digitar *224* DEPOIS que o cliente disser que abriu ou instalou.\n\n"
        "Se o cliente disser que acessou, oriente a digitar **224**. Depois disso, aguarde 4 segundos e diga que o teste dura 3 horas.\n"
        "NÃO envie valores agora, só depois de 3 horas ou se o cliente pedir.\n\n"
        "Durante o teste, agende lembrete com 30 minutos e mensagem informando que canais como *Premiere, HBO Max, Disney+* só funcionam perto dos eventos ao vivo.\n"
        "Se o teste acabar (após 3h), envie os planos:\n"
        "💰 Planos disponíveis:\n"
        "1 mês – R$ 26,00\n2 meses – R$ 47,00\n3 meses – R$ 68,00\n6 meses – R$ 129,00\n1 ano – R$ 185,00\n\n"
        "Pagamento: Pix (CNPJ separado) ou cartão.\n"
        "PIX (CNPJ): 46.370.366/0001-97\n💳 Cartão: https://mpago.la/2Nsh3Fq\n\n"
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

def agendar_mensagens(numero):
    time.sleep(1800)
    mensagem1 = (
        "⏱️ Já se passaram 30 minutos desde que você recebeu o teste.\n"
        "Conseguiu assistir direitinho? Precisa de ajuda? 💬"
    )
    historico_conversas[numero].append(f"IA: {mensagem1}")
    enviar_whatsapp(numero, mensagem1)

    time.sleep(3600)
    mensagem2 = (
        "📢 Alguns canais como *Premiere, HBO Max, Disney+* só abrem minutos antes dos eventos ao vivo.\n"
        "Se estiverem fechados, fique tranquilo: eles ativam automaticamente perto do horário. 😉"
    )
    historico_conversas[numero].append(f"IA: {mensagem2}")
    enviar_whatsapp(numero, mensagem2)

    time.sleep(5400)
    mensagem3 = (
        "⏳ Seu teste terminou! Espero que tenha gostado. 😄\n\n"
        "💰 Planos disponíveis:\n"
        "1 mês – R$ 26,00\n2 meses – R$ 47,00\n3 meses – R$ 68,00\n6 meses – R$ 129,00\n1 ano – R$ 185,00\n\n"
        "Formas de pagamento:\n"
        "PIX (CNPJ): 46.370.366/0001-97\n"
        "💳 Cartão: https://mpago.la/2Nsh3Fq\n\n"
        "Se quiser assinar, me avise! 📲"
    )
    historico_conversas[numero].append(f"IA: {mensagem3}")
    enviar_whatsapp(numero, mensagem3)

def enviar_whatsapp(numero, mensagem):
    print(f"[Agendado para {numero}] {mensagem}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
