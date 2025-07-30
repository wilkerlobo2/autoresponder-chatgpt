def responder_regra_manutencao(msg):
    msg = msg.lower()

    # Regras fixas por modelo de TV
    if "roku" in msg:
        return "Vamos testar com o app Xcloud na sua Roku. Se não funcionar, usamos o OTT Player."
    if "samsung" in msg and "nova" in msg:
        return "Use o app Xcloud. Caso não funcione, envie a foto do QR code do Duplecast."
    if "lg" in msg:
        return "Vamos usar o app Xcloud. Se não funcionar, você pode testar com Duplecast (QR code) ou SmartOne (MAC)."
    if "android" in msg or "tv box" in msg:
        return "Perfeito, vamos usar o app Xtream IPTV Player. Aguarde que já vou gerar o login."
    if "philips" in msg or "aoc" in msg:
        return "Instale o OTT Player ou Duplecast. Me envie o QR code do app escolhido."
    if "computador" in msg or "pc" in msg:
        return "Você pode assistir pelo PC. Te envio o link e login. Qual navegador você usa?"
    if "iphone" in msg or "ios" in msg:
        return "Baixe o app Smarters Player Lite. Vou gerar seu login!"
    if msg in ["oi", "olá", "bom dia", "boa tarde", "boa noite"]:
        return "Olá! Tudo certo 😊 Me diga o modelo da sua TV ou aparelho que vou te orientar certinho."

    # Palavras que indicam que o cliente quer saber sobre preços ou pagar
    palavras_pagamento = ["plano", "planos", "valor", "valores", "preço", "preços", "mensalidade", "pagar", "pagamento", "pix", "cartão"]
    if any(p in msg for p in palavras_pagamento):
        return (
            "*Planos de Assinatura:*\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$ 47,00 - 2 meses\n"
            "✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n"
            "✅ R$ 185,00 - 1 ano\n\n"
            "*Formas de pagamento:*\n"
            "🔹 *PIX:* 41.638.407/0001-26 (Banco C6)\n"
            "🔹 *CNPJ:* Axel Castelo\n\n"
            "💳 Para pagar com *cartão*, use o link:\nhttps://link.mercadopago.com.br/cplay"
        )

    return None  # Se não bater nenhuma regra, usa IA
