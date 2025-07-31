from flask import Flask, request, jsonify
import openai
import re
import requests

app = Flask(__name__)

openai.api_key = "SUA_API_KEY"  # Troque pela sua chave da OpenAI

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

DISPOSITIVOS = {
    "roku": "xcloud",
    "samsung": "xcloud",
    "lg": "xcloud",
    "philco": "xcloud",
    "android": "xtream iptv player",
    "tv box": "xtream iptv player",
    "celular": "xtream iptv player",
    "projetor": "xtream iptv player",
    "iphone": "smarters player lite",
    "ios": "smarters player lite",
    "computador": "smarters player lite",
    "fire stick": "xtream iptv player",
    "aoc": "ott player ou duplecast",
    "philips": "ott player ou duplecast",
    "smartone": "smartone"
}

def gerar_boas_vindas(nome):
    if nome.startswith("+55"):
        return (
            "Olá! 👋\n"
            "Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries* no seu dispositivo preferido. 📺🍿\n"
            "Vamos começar seu teste gratuito?\n\n"
            "Me diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        )
    return None

def gerar_login(webhook):
    try:
        r = requests.get(webhook, timeout=10)
        if r.status_code == 200:
            data = r.json()
            username = data.get("username", "")
            password = data.get("password", "")
            dns = data.get("dns", "")
            msg = f"*Usuário:* `{username}`\n*Senha:* `{password}`"
            if dns:
                msg += f"\n*DNS:* `{dns}`"

            aviso = ""
            if re.search(r"[IlO0]", username):
                aviso += "\n\n⚠️ *Atenção com o login:*\n"
                if "I" in username:
                    aviso += "✅ Letra *I* de *Índia*\n"
                if "l" in username:
                    aviso += "✅ Letra *l* minúscula de *lápis*\n"
                if "O" in username:
                    aviso += "✅ Letra *O* de *Ovo*\n"
                if "0" in username:
                    aviso += "✅ Número *0* (zero)\n"
                aviso += "Digite exatamente como enviado, respeitando maiúsculas e minúsculas."

            return msg + "\n\n⏳ *Seu teste dura 3 horas.*" + aviso
        else:
            return "❌ Erro ao gerar o login. Tente novamente em instantes."
    except:
        return "⚠️ Erro ao conectar com o servidor de testes."

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    nome = data.get("name", "")
    msg = data.get("message", "").lower()
    resposta = []

    # Boas-vindas para novos contatos
    boasvindas = gerar_boas_vindas(nome)
    if boasvindas:
        resposta.append({"message": boasvindas})

    # Reconhece dispositivo
    for chave, app in DISPOSITIVOS.items():
        if chave in msg:
            if app == "xcloud":
                resposta.append({"message": "✅ Baixe o app *Xcloud* (ícone verde e preto) na sua TV e me avise quando estiver instalado para liberar o login de teste."})
            elif app == "xtream iptv player":
                resposta.append({"message": "✅ Baixe o app *Xtream IPTV Player* no seu Android, TV box ou celular. Me avise quando tiver instalado para liberar o teste!"})
            elif app == "smarters player lite":
                resposta.append({"message": "✅ Baixe o *Smarters Player Lite* no seu iPhone ou computador. Me avise quando instalar para liberar o login!"})
            elif "ott" in app or "duplecast" in app:
                resposta.append({"message": "✅ Instale o *OTT Player* ou *Duplecast*, depois envie a *foto do QR Code* da tela para ativação manual."})
            elif app == "smartone":
                resposta.append({"message": "✅ Me envie o *código MAC* que aparece no app *SmartOne IPTV* para ativar manualmente."})

    # Cliente disse que já instalou
    if any(p in msg for p in ["instalei", "baixei", "baixado", "foi", "pronto"]):
        if "samsung" in msg and "antiga" in msg:
            login = gerar_login(WEBHOOK_GERAL)
            resposta.append({"message": f"Aqui está seu login para Smart STB:\n\n{login}"})
        elif any(x in msg for x in ["iphone", "ios", "computador"]):
            login = gerar_login(WEBHOOK_GERAL)
            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        elif any(x in msg for x in ["xcloud", "roku", "samsung", "lg", "philco"]):
            login = gerar_login(WEBHOOK_XCLOUD)
            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        else:
            login = gerar_login(WEBHOOK_GERAL)
            resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})

        resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})

    # Confirmação de que funcionou
    if "deu certo" in msg:
        resposta.append({"message": "✅ Que bom! Aproveite os canais, filmes e séries. Qualquer dúvida estou por aqui!"})
    
    # Quando não funcionou
    if "não funcionou" in msg or "erro" in msg:
        resposta.append({"message": "❌ Verifique se digitou tudo corretamente (respeitando maiúsculas e minúsculas). Se puder, envie uma foto da tela para te ajudar melhor."})

    # Fim do teste
    if "acabou" in msg or "terminou" in msg or "teste acabou" in msg:
        resposta.append({"message": (
            "⏰ Seu teste terminou!\n\n"
            "Quer continuar assistindo? Aqui estão nossos planos:\n\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$ 47,00 - 2 meses\n"
            "✅ R$ 68,00 - 3 meses\n"
            "✅ R$ 129,00 - 6 meses\n"
            "✅ R$ 185,00 - 1 ano\n\n"
            "*PIX:* 41.638.407/0001-26\n"
            "*Banco:* C6 (CNPJ: Axel Castelo)\n\n"
            "*💳 Cartão:* https://link.mercadopago.com.br/cplay"
        )})

    # Explicação do que é IPTV
    if "iptv" in msg or "como funciona" in msg:
        resposta.append({"message": (
            "📺 *IPTV* é TV por internet! Você assiste ao vivo, filmes e séries direto no seu app, sem antenas nem cabos. Basta instalar o app, digitar seu login e curtir!"
        )})

    # Se nenhuma resposta foi gerada
    if not resposta:
        resposta.append({"message": "Me diga qual é o modelo da sua TV ou celular para indicar o app ideal. 📲"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
