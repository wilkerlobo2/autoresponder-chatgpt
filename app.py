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

    # Guarda mensagem do cliente no histórico
    historico_conversas[numero].append(f"Cliente: {mensagem}")
    contexto = "\n".join(historico_conversas[numero][-15:])

    # Códigos de teste reconhecidos
    codigos_teste = ["224", "555", "91", "88", "871", "98", "94"]

    # Se o cliente já digitou um código e agora confirmou que funcionou
    codigo_digitado = any(f"Cliente: {c}" in contexto for c in codigos_teste)
    resposta_afirmativa = any(p in mensagem for p in ["deu certo", "acessou", "funcionou", "sim", "consegui", "tudo certo"])
    resposta_negativa = any(p in mensagem for p in ["não", "nao", "n consegui", "não funcionou", "n deu certo", "nao deu certo"])

    if codigo_digitado and resposta_afirmativa:
        texto = "Perfeito! Aproveite seu teste. 😊"
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Se o cliente disse que não conseguiu acessar após um código
    if codigo_digitado and resposta_negativa:
        texto = (
            "Vamos resolver isso! Verifique se digitou *exatamente* como enviado.\n"
            "Atenção às *letras maiúsculas e minúsculas* e aos caracteres parecidos (*I* vs *l*, *O* vs *0*).\n"
            "Pode me enviar uma *foto da tela* mostrando como você está digitando? 📷"
        )
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # FOTO / QR / MAC: pedir qual app foi baixado (não dá pra identificar imagem)
    if any(k in mensagem for k in ["foto", "qrcode", "qr code", "qr-code", "qr", "mac:", "endereço mac", "endereco mac", "mostrei a tela"]):
        texto_foto = (
            "Entendi! Como não consigo identificar imagens aqui, me diga por favor **qual aplicativo você está usando**: "
            "*Duplecast*, *SmartOne*, *OTT Player*, *Xcloud (ícone verde e preto)*, *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *Vu IPTV Player*? 😉"
        )
        historico_conversas[numero].append(f"IA: {texto_foto}")
        return jsonify({"replies": [{"message": texto_foto}]})

    # ======== RESPOSTAS DETERMINÍSTICAS ========

    # Android (inclui Philips) – primeira resposta SEM link
    if any(word in mensagem for word in ["android", "tv box", "projetor", "celular android", "celular", "philips"]):
        texto_android = (
            "Para Android, baixe o app **Xtream IPTV Player** 📺👇📲 (recomendado).\n"
            "Também pode usar: *9Xtream*, *XCIPTV* ou *Vu IPTV Player*.\n"
            "Me avise quando instalar para eu enviar seu login."
        )
        historico_conversas[numero].append(f"IA: {texto_android}")
        return jsonify({"replies": [{"message": texto_android}]})

    # Se o cliente disser que NÃO consegue baixar da loja (aí sim mandar link)
    frases_sem_baixar = [
        "não consigo baixar", "nao consigo baixar", "não acho na loja", "nao acho na loja",
        "não encontra na loja", "nao encontra na loja", "não tem na loja", "nao tem na loja",
        "tem link", "manda o link", "baixar por link", "link alternativo", "apk", "aptoide", "ntdown", "downloader"
    ]
    if any(f in mensagem for f in frases_sem_baixar):
        texto_link = (
            "🔔 **AÇÃO MANUAL NECESSÁRIA**: cliente precisa de link alternativo.\n"
            "Baixe por link (Chrome/Downloader/NTDOWN): http://xwkhb.info/axc\n"
            "Depois que abrir o app, me avise para eu enviar o seu login."
        )
        historico_conversas[numero].append(f"IA: {texto_link}")
        return jsonify({"replies": [{"message": texto_link}]})

    # Dispositivos de Xcloud (Samsung, LG, Roku, Philco nova) – com alternativas
    if any(word in mensagem for word in ["samsung", "lg", "roku", "philco nova", "xcloud"]):
        texto_xcloud = (
            "Para sua TV, use o **Xcloud (ícone verde e preto)** 📺✨ *preferencial*.\n"
            "Se preferir, alternativas: *OTT Player*, *Duplecast* ou *SmartOne*.\n"
            "Instale e me avise para eu enviar seu login. Lembre-se: o teste gratuito dura **3 horas**."
        )
        historico_conversas[numero].append(f"IA: {texto_xcloud}")
        return jsonify({"replies": [{"message": texto_xcloud}]})

    # ======== OUTRAS REGRAS ========

    # Regra especial para PC (link de download)
    if any(p in mensagem for p in ["pc", "computador", "notebook", "windows", "macbook"]):
        texto_pc = (
            "Para PC, você precisa baixar o app usando o link:\n"
            "https://7aps.online/iptvsmarters\n\n"
            "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
        )
        historico_conversas[numero].append(f"IA: {texto_pc}")
        return jsonify({"replies": [{"message": texto_pc}]})

    # Detectar confirmação de instalação (decide o código pelo contexto)
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        ultimas = [m for m in historico_conversas[numero][-6:] if m.startswith("Cliente:")]
        mensagem_relevante = " ".join(ultimas).lower()

        if ("xcloud" in mensagem_relevante) or any(d in mensagem_relevante for d in ["samsung", "lg", "roku", "philco nova"]):
            codigo = "91"
        elif any(app in mensagem_relevante for app in ["xtream", "9xtream", "xciptv", "vu iptv", "android", "tv box", "celular", "projetor", "philips"]):
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

    # Gatilho se o cliente digita um código de teste
    if mensagem.strip() in codigos_teste:
        resposta.append({"message": "🔓 Gerando seu login de teste, só um instante..."})
        return jsonify({"replies": resposta})

    # Prompt da IA (casos gerais)
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado. "
        "Use emojis e evite textos gigantes: divida em mensagens curtas. "
        "O teste gratuito dura **3 horas**.\n\n"
        "Se o cliente pedir valores, envie os planos:\n"
        "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00.\n"
        "Pagamento: Pix (envie o CNPJ sozinho na mensagem seguinte) ou Cartão: https://mpago.la/2Nsh3Fq.\n\n"
        "Fluxos especiais:\n"
        "- Duplecast: Start > Português > Brasil > Fuso -03 > Minha duplecast; peça **foto do QR**; depois peça digitar **871**.\n"
        "- SmartOne: peça **MAC** ou **foto com o MAC**; depois **871**.\n"
        "- OTT Player: peça **foto do QR**; depois **871**.\n"
        "- Se enviar foto/QR/MAC, diga que não dá para identificar imagem e pergunte **qual aplicativo** está usando; siga o fluxo correspondente.\n"
        "- Se não souber a TV ou enviar foto da tela: diga '**🔔 AÇÃO MANUAL NECESSÁRIA**: vou analisar a foto e te direcionar certinho.'\n"
        "- Se mandar áudio: diga que não consegue interpretar e continue por texto.\n\n"
        f"Histórico (últimas):\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Responda agora seguindo TODAS as instruções."
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

        # Pix separado se mencionar pagamento/valor/planos
        if any(p in mensagem for p in ["pix", "pagamento", "valor", "quanto", "plano", "planos", "preço", "preco"]):
            resposta.append({"message": "Pix (CNPJ): 46.370.366/0001-97"})

    except Exception as e:
        resposta.append({"message": f"⚠️ Erro ao gerar resposta: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
