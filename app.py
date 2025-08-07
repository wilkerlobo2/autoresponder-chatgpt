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

    # Verifica se o cliente já digitou um código antes
    codigos_teste = ["224", "555", "91", "88", "871", "98", "94"]
    codigo_digitado = any(f"Cliente: {c}" in contexto for c in codigos_teste)
    resposta_afirmativa = any(p in mensagem for p in ["deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo"])
    resposta_negativa = any(p in mensagem for p in ["não", "nao", "n consegui", "não funcionou", "n deu certo"])

    if codigo_digitado and resposta_afirmativa:
        texto = "Perfeito! Aproveite seu teste. 😊"
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Novo: Se cliente disser que não conseguiu acessar APÓS digitar algum código de teste
    if codigo_digitado and resposta_negativa:
        texto = (
            "Vamos resolver isso! Por favor, verifique se digitou os dados exatamente como enviados.\n\n"
            "Preste atenção nas *letras maiúsculas e minúsculas*, e nos caracteres parecidos como *I (i maiúsculo)* e *l (L minúsculo)*, ou *O (letra)* e *0 (zero)*.\n\n"
            "Me envie uma *foto da tela* mostrando como você está digitando para que eu possa te ajudar melhor. 📷"
        )
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Detectar confirmação de instalação
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        ultimas = [m for m in historico_conversas[numero][-6:] if m.startswith("Cliente:")]
        mensagem_relevante = " ".join(ultimas).lower()

        if "xcloud" in mensagem_relevante or "samsung" in mensagem_relevante:
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
        elif any(a in mensagem_relevante for a in ["duplecast", "smartone", "ott"]):
            codigo = "871"
        else:
            codigo = "91"

        texto = f"Digite *{codigo}* aqui na conversa para receber seu login. 😉"
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
        return jsonify({"replies": resposta})

    # Gatilho de login automático
    if mensagem.strip() in codigos_teste:
        resposta.append({"message": "🔓 Gerando seu login de teste, só um instante..."})
        return jsonify({"replies": resposta})

    # Prompt da IA com instruções atualizadas
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use emojis criativos sempre que indicar um aplicativo. NÃO envie links de IPTV ou imagens.\n\n"
        "🕒 Informe sempre que o teste gratuito dura *3 horas*.\n"
        "Se o cliente perguntar sobre valores ou preços, envie os planos:\n"
        "💰 Planos disponíveis:\n"
        "1 mês – R$ 26,00\n2 meses – R$ 47,00\n3 meses – R$ 68,00\n6 meses – R$ 129,00\n1 ano – R$ 185,00\n\n"
        "💳 Formas de pagamento:\nPix (envie o CNPJ sozinho): 46.370.366/0001-97\n"
        "Cartão: https://mpago.la/2Nsh3Fq\n\n"
        "Quando o cliente disser o aparelho (TV LG, Roku, iPhone, etc), diga QUAL app ele deve baixar e diga:\n"
        "'Baixe o app [NOME] 📺👇📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"
        "📱 Android: Xtream IPTV Player (ou 9xtream, XCIPTV, Vu IPTV)\n"
        "📺 Samsung, LG, Roku, Philco nova: app Xcloud\n"
        "📲 iPhone: Smarters Player Lite (App Store)\n"
        "🖥️ PC: https://7aps.online/iptvsmarters\n"
        "📸 Se o cliente disser que tem o Duplecast:\n"
        "- Envie passo a passo: Start > Português > Brasil > Fuso horário -03 > Minha duplecast\n"
        "- Peça foto do QR code de perto\n"
        "- Após foto, diga para digitar 871\n"
        "📸 Se já tem o Duplecast, pule os passos, peça a foto do QR\n"
        "📸 Se for SmartOne, peça MAC ou foto da tela com MAC, depois peça para digitar 871\n"
        "📸 Se for OTT Player, peça foto do QR, depois peça para digitar 871\n"
        "❓ Se o cliente disser que não sabe a TV ou mandar foto da tela, peça a foto e aguarde atendimento humano\n"
        "🔇 Se mandar áudio, diga que não pode interpretar, mas pode continuar normalmente\n\n"
        f"Histórico:\n{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
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

        if any(p in mensagem for p in ["pix", "pagamento", "valor", "quanto", "plano"]):
            resposta.append({"message": "Pix (CNPJ): 46.370.366/0001-97"})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
