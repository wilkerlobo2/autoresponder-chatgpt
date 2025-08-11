from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
historico_conversas = {}

# Constantes
CODIGOS_TESTE = ["224", "555", "91", "88", "871", "98", "94"]

MSG_ANDROID = (
    "📱 Para Android, baixe preferencialmente o *Xtream IPTV Player* 📺⬇️📲.\n"
    "Outras opções: *9Xtream*, *XCIPTV* ou *Stream IPTV Player*.\n\n"
    "Se não conseguir baixar, me avise. Posso te ensinar a instalar pelo navegador usando este link:\n"
    "➡️ http://xwkhb.info/axc"
)

MSG_XCLOUD = (
    "📺 Para sua TV, baixe o app *Xcloud verde com preto* 📺⬇️📲.\n"
    "Alternativas: *OTT Player*, *Duplecast* ou *SmartOne*.\n"
    "Me avise quando instalar para que eu envie seu login."
)

MSG_ATENDIMENTO_HUMANO = (
    "🚨📣 ATENDIMENTO HUMANO NECESSÁRIO 📣🚨\n"
    "Um atendente vai te ajudar em instantes."
)

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    query = data.get("query", {})
    numero = query.get("sender", "").strip()
    mensagem = query.get("message", "").strip().lower()
    resposta = []

    if not numero or not mensagem:
        return jsonify({"replies": [{"message": "⚠️ Mensagem inválida recebida."}]})

    # Boas-vindas
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

    codigo_digitado = any(f"Cliente: {c}" in contexto for c in CODIGOS_TESTE)
    resposta_afirmativa = any(p in mensagem for p in ["deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo"])
    resposta_negativa = any(p in mensagem for p in ["não", "nao", "n consegui", "não funcionou", "n deu certo"])

    # Cliente já confirmou login
    if codigo_digitado and resposta_afirmativa:
        texto = "Perfeito! Aproveite seu teste. 😊"
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Cliente não conseguiu acessar
    if codigo_digitado and resposta_negativa:
        texto = (
            "Vamos resolver isso! Verifique se digitou exatamente como enviado.\n"
            "Atenção às *letras maiúsculas/minúsculas* e caracteres parecidos (*I/l*, *O/0*).\n"
            "Me envie uma *foto da tela* mostrando como está digitando. 📷"
        )
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Detectar confirmação de instalação
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        ultimas = [m for m in historico_conversas[numero][-6:] if m.startswith("Cliente:")]
        msg_relevante = " ".join(ultimas).lower()

        if "philips" in msg_relevante or "android" in msg_relevante:
            texto = MSG_ANDROID
            codigo = "555"
        elif "xcloud" in msg_relevante or "samsung" in msg_relevante or "lg" in msg_relevante or "roku" in msg_relevante or "philco" in msg_relevante:
            texto = MSG_XCLOUD
            codigo = "91"
        else:
            texto = MSG_ATENDIMENTO_HUMANO
            codigo = None

        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
        if codigo:
            resposta.append({"message": f"Digite *{codigo}* aqui na conversa para receber seu login. 😉"})
        return jsonify({"replies": resposta})

    # Cliente digitou código
    if mensagem.strip() in CODIGOS_TESTE:
        resposta.append({"message": "🔓 Gerando seu login de teste, só um instante..."})
        return jsonify({"replies": resposta})

    # Cliente enviou foto
    if any(p in mensagem for p in ["foto", "imagem", "print", "foto do", "print do"]):
        texto = "Não consigo identificar imagens. Qual aplicativo você baixou? (Xcloud verde com preto, OTT Player, Duplecast ou SmartOne)"
        return jsonify({"replies": [{"message": texto}]})

    # Prompt IA
    prompt = (
        "Você é um atendente de IPTV no WhatsApp. Seja rápido, objetivo e use emojis.\n"
        "Philips = Android.\n"
        "Xcloud sempre deve ser referido como 'Xcloud verde com preto'.\n"
        "Para Android: enfatize Xtream IPTV Player, mas liste 9Xtream, XCIPTV e Stream IPTV Player como opções.\n"
        "Se não conseguir instalar, ensine a usar o link http://xwkhb.info/axc.\n"
        "Se mandar foto, pergunte qual app baixou antes de prosseguir.\n"
        "Histórico:\n"
        f"{contexto}\n\nMensagem mais recente: '{mensagem}'\n\nResponda:"
    )

    try:
        resp_ia = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        texto = resp_ia.choices[0].message.content.strip()
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Erro: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
