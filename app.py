from flask import Flask, request, jsonify
import openai
import random
import time

app = Flask(__name__)

openai.api_key = "SUA_CHAVE_DA_API_OPENAI"

# Dicionário para armazenar estado por número
estado_cliente = {}

@app.route("/", methods=["POST"])
def responder():
    data = request.json
    mensagem = data.get("query", {}).get("message", "").strip().lower()
    numero = data.get("query", {}).get("sender", "")

    respostas = []

    # Verifica se é mídia (imagem, áudio, etc.)
    if any(palavra in mensagem for palavra in ["audio", "foto", "imagem", "vídeo"]):
        respostas.append("📎 Recebi uma mídia! Vou deixar para meu suporte analisar e já já ele te responde manualmente, ok?")
        return jsonify({"replies": [{"message": r} for r in respostas]})

    # Se ainda não tem estado, inicia
    if numero not in estado_cliente:
        estado_cliente[numero] = {
            "etapa": "inicio",
            "app": None,
            "tv": None,
            "esperando_instalacao": False,
            "login_enviado": False,
            "inicio_teste": None
        }

    estado = estado_cliente[numero]

    # IA interpreta o tipo de TV/dispositivo
    if estado["etapa"] == "inicio":
        prompt = f"""
        O cliente enviou: "{mensagem}"

        Interprete a marca/modelo da TV ou o dispositivo (ex: Roku, Android, Samsung nova, LG, iPhone, Fire Stick etc).
        Diga apenas qual app ele deve instalar primeiro. Responda de forma natural e criativa, como se fosse um humano.
        Em seguida, diga: "Quando terminar de instalar, me avisa por aqui 😉"
        """
        resposta_ia = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        resposta = resposta_ia.choices[0].message.content.strip()
        estado["etapa"] = "aguardando_instalacao"
        respostas.append(resposta)
        return jsonify({"replies": [{"message": r} for r in respostas]})

    # Cliente confirma que instalou o app
    if estado["etapa"] == "aguardando_instalacao" and any(p in mensagem for p in ["instalei", "já instalei", "baixei", "já baixei", "pronto"]):
        # Decide qual número mandar
        if "xcloud" in mensagem or "roku" in mensagem or "samsung nova" in mensagem or "lg" in mensagem:
            numero_teste = "91"
        elif "iphone" in mensagem or "ios" in mensagem:
            numero_teste = "224"
        elif "samsung antigo" in mensagem or "smart stb" in mensagem or "88" in mensagem:
            numero_teste = "88"
        else:
            numero_teste = "221"

        estado["numero_teste"] = numero_teste
        estado["etapa"] = "aguardando_envio_login"

        respostas.append(f"Perfeito! 😄 Agora digite *{numero_teste}* aqui na conversa para gerar seu login de teste!")
        return jsonify({"replies": [{"message": r} for r in respostas]})

    # Após login enviado (detecta número digitado)
    if estado["etapa"] == "aguardando_envio_login" and mensagem in ["221", "224", "91", "88"]:
        estado["login_enviado"] = True
        estado["inicio_teste"] = time.time()
        estado["etapa"] = "aguardando_confirmacao"

        respostas.append("Login enviado! ✅ Daqui a pouco volto pra saber se funcionou!")
        return jsonify({"replies": [{"message": r} for r in respostas]})

    # 30 minutos depois, verifica se deu certo
    if estado["etapa"] == "aguardando_confirmacao" and estado["login_enviado"]:
        tempo_passado = time.time() - estado["inicio_teste"]
        if tempo_passado > 1800 and tempo_passado < 7200:  # Entre 30 min e 2h
            respostas.append("E aí, deu tudo certo com o teste? 🎬")
            respostas.append("Caso não tenha funcionado, me diga o que apareceu ou mande uma foto da tela pra eu te ajudar.")
            estado["etapa"] = "aguardando_fim_teste"
            return jsonify({"replies": [{"message": r} for r in respostas]})

    # Final do teste (após 3h)
    if estado["etapa"] == "aguardando_fim_teste" and estado["inicio_teste"]:
        tempo_total = time.time() - estado["inicio_teste"]
        if tempo_total > 10800:  # 3h
            respostas.append("⏰ Seu teste gratuito de IPTV chegou ao fim!")
            respostas.append("Se você curtiu a programação, pode assinar agora mesmo com a gente! 😄")
            respostas.append(
                "*Planos disponíveis:*\n"
                "- R$ 26,00 – 1 mês\n"
                "- R$ 47,00 – 2 meses\n"
                "- R$ 68,00 – 3 meses\n"
                "- R$ 129,00 – 6 meses\n"
                "- R$ 185,00 – 1 ano\n\n"
                "*Formas de pagamento:*\n"
                "- 💳 Cartão: [link do pagamento]\n"
                "- 💸 PIX (CNPJ): 00.000.000/0001-00"
            )
            estado["etapa"] = "fim"
            return jsonify({"replies": [{"message": r} for r in respostas]})

    # Resposta padrão
    respostas.append("🤖 Recebi sua mensagem! Se quiser fazer um teste IPTV, me diga o modelo da sua TV ou aparelho.")
    return jsonify({"replies": [{"message": r} for r in respostas]})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
