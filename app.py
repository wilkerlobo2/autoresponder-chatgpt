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
            "Vamos resolver isso! Por favor, verifique se digitou os dados exatamente como enviados.\n\n"
            "Atenção às *letras maiúsculas e minúsculas* e aos caracteres parecidos: *I (i maiúsculo)* vs *l (L minúsculo)*, e *O (letra)* vs *0 (zero)*.\n\n"
            "Me envie uma *foto da tela* mostrando como você está digitando para eu te orientar melhor. 📷"
        )
        historico_conversas[numero].append(f"IA: {texto}")
        return jsonify({"replies": [{"message": texto}]})

    # Regra especial para PC (link de download)
    if any(p in mensagem for p in ["pc", "computador", "notebook", "windows", "macbook"]):
        texto_pc = (
            "Para PC, você precisa baixar o app usando o link:\n"
            "https://7aps.online/iptvsmarters\n\n"
            "Depois me avise quando abrir o link para que eu possa enviar o seu login. ☺️"
        )
        historico_conversas[numero].append(f"IA: {texto_pc}")
        return jsonify({"replies": [{"message": texto_pc}]})

    # FOTO / QR / MAC: pedir qual app foi baixado (não dá pra identificar imagem)
    if any(k in mensagem for k in ["foto", "qrcode", "qr code", "qr-code", "qr", "mac: ", "endereço mac", "endereco mac", "mostrei a tela"]):
        texto_foto = (
            "Entendi! Como não consigo identificar imagens aqui, me diga por favor **qual aplicativo você está usando**: "
            "*Duplecast*, *SmartOne*, *OTT Player*, *Xcloud (ícone verde e preto)*, *Xtream IPTV Player*, *9Xtream*, *XCIPTV* ou *Vu IPTV Player*? 😉"
        )
        historico_conversas[numero].append(f"IA: {texto_foto}")
        return jsonify({"replies": [{"message": texto_foto}]})

    # Detectar confirmação de instalação (decidir código por contexto recente)
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "feito", "já instalei", "ja instalei", "acessado", "abri"]):
        ultimas = [m for m in historico_conversas[numero][-6:] if m.startswith("Cliente:")]
        mensagem_relevante = " ".join(ultimas).lower()

        # Xcloud em qualquer device que usa Xcloud
        if "xcloud" in mensagem_relevante or "samsung" in mensagem_relevante or "roku" in mensagem_relevante or "lg" in mensagem_relevante or "philco nova" in mensagem_relevante:
            codigo = "91"
        # Android (inclui PHILIPS como Android)
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

    # Prompt da IA com TODAS instruções
    prompt = (
        "Você é um atendente de IPTV via WhatsApp. Seja direto, simples e educado como uma linha de produção. "
        "Use bastante emojis criativos sempre que indicar um aplicativo. NÃO envie links de IPTV ou imagens.\n\n"
        "NÃO escreva textos enormes: **divida em mensagens curtas** quando fizer sentido.\n"
        "🕒 O teste gratuito dura **3 horas** (nunca 24h).\n\n"

        "💰 Se o cliente pedir valores, envie os planos:\n"
        "1 mês – R$ 26,00 | 2 meses – R$ 47,00 | 3 meses – R$ 68,00 | 6 meses – R$ 129,00 | 1 ano – R$ 185,00\n"
        "💳 Pagamento: Pix (envie o CNPJ sozinho na mensagem seguinte) ou Cartão (link seguro)\n"
        "Pix (CNPJ): **46.370.366/0001-97**\n"
        "Cartão: https://mpago.la/2Nsh3Fq\n\n"

        "📲 Quando o cliente disser o aparelho (ex: TV LG, Roku, Android, iPhone, Computador), diga QUAL app baixar e use a frase:\n"
        "'Baixe o app [NOME] 📺👇📲 para [DISPOSITIVO]! Me avise quando instalar para que eu envie o seu login.'\n\n"

        "🏷️ **Dispositivos que usam Xcloud**: Samsung, LG, Roku, Philco nova —> **Xcloud (ícone verde e preto)** em destaque.\n"
        "   ➕ Ofereça como alternativas: **OTT Player**, **Duplecast**, **SmartOne** (mas mantenha o Xcloud como preferência).\n\n"

        "🤖 **Android (inclui TVs PHILIPS)**: indique **Xtream IPTV Player** (ênfase) e, como opções, **9Xtream**, **XCIPTV**, **Vu IPTV Player**.\n"
        "   Se o cliente **não conseguir baixar da loja**, pergunte se pode baixar por link (Chrome/Downloader/NTDOWN) e instrua usar **http://xwkhb.info/axc**.\n"
        "   Depois que entrar no app por esse link, peça para **AGUARDAR ATENDIMENTO HUMANO** para envio do login e **comece a mensagem com**: "
        "   '🚨 ATENDIMENTO HUMANO NECESSÁRIO: ...' para ficar visível sem abrir a conversa.\n\n"

        "🍏 **iPhone/iOS**: Smarters Player Lite (ícone azul, App Store). Após instalar, peça para digitar **224** quando for o momento do teste.\n"
        "🖥️ **PC**: peça para baixar o app em https://7aps.online/iptvsmarters. Após instalar, peça para digitar **224** quando for o momento do teste.\n\n"

        "🧩 **Duplecast**: se o cliente disser que baixou, enviar:\n"
        "- Start > Português > Brasil > Fuso horário -03 > Minha duplecast\n"
        "- Pedir **foto do QR code** de perto.\n"
        "- Depois da foto, pedir para digitar **871** (teste via link m3u).\n"
        "Se ele **já tem** o Duplecast, pule os passos e peça direto a **foto do QR**, depois **871**.\n\n"

        "🧩 **SmartOne**: peça **foto da tela com o MAC** ou o **MAC** em texto; depois peça para digitar **871**.\n"
        "🧩 **OTT Player**: peça **foto do QR**; depois **871**.\n\n"

        "🖼️ Se o cliente enviar **foto/QR/MAC**, diga que não consegue identificar imagens aqui e **pergunte qual aplicativo** está usando; "
        "em seguida **siga o fluxo do app que ele informar**.\n\n"

        "❓ Se o cliente disser que **não sabe a TV** ou mandar foto da tela, peça a foto e diga: "
        "'🚨 ATENDIMENTO HUMANO NECESSÁRIO: vou analisar a foto e te direcionar certinho.'\n"
        "🔇 Se mandar **áudio**, diga que você **não pode interpretar áudios**, mas que pode continuar por texto normalmente.\n\n"

        f"Histórico da conversa (últimas mensagens):\n{contexto}\n\n"
        f"Mensagem mais recente do cliente: '{mensagem}'\n\n"
        "Responda agora seguindo TODAS as instruções acima."
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
