from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re
import requests
import threading
import time

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WEBHOOK_XCLOUD = "https://a.opengl.in/chatbot/check/?k=66b125d558"
WEBHOOK_GERAL = "https://painelacesso1.com/chatbot/check/?k=76be279cb5"

historico_conversas = {}
testes_em_andamento = {}
dispositivos_detectados = {}

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

def agendar_mensagens(numero):
    def tarefa():
        time.sleep(1800)  # 30 minutos
        historico_conversas[numero].append("IA: Está funcionando?")
        testes_em_andamento[numero].append(
            {"message": "Tudo certo aí? 😊 Só passando pra ver se conseguiu usar direitinho. Se tiver dúvidas, é só me chamar!"}
        )
        time.sleep(5400)  # até 3 horas no total
        historico_conversas[numero].append("IA: Enviando planos.")
        planos = (
            "*Seu teste terminou!*\n\n"
            "Gostou do serviço? Temos planos super acessíveis pra continuar:\n\n"
            "✅ R$ 26,00 - 1 mês\n"
            "✅ R$47,00 - 2 meses\n"
            "✅ R$68,00 - 3 meses\n"
            "✅ R$129,00 - 6 meses\n"
            "✅ R$185,00 - 1 ano\n\n"
            "💳 Aceitamos Pix e cartão.\n"
            "Deseja garantir o seu agora? 😄"
        )
        testes_em_andamento[numero].append({"message": planos})

    t = threading.Thread(target=tarefa)
    t.start()

def detectar_dispositivo(msg):
    msg = msg.lower()
    if any(x in msg for x in ["roku", "lg", "samsung", "philco", "xcloud"]):
        return "xcloud"
    if any(x in msg for x in ["android", "tv box", "celular", "fire stick", "xtream"]):
        return "xtream"
    if any(x in msg for x in ["iphone", "ios", "computador", "pc", "macbook", "notebook", "smarters"]):
        return "smarters"
    if any(x in msg for x in ["aoc", "philips", "ott", "duplecast"]):
        return "qr"
    if "smartone" in msg:
        return "mac"
    return None

@app.route("/", methods=["POST"])
def responder():
    data = request.get_json()
    nome = data.get("name", "")
    numero = nome.strip()
    mensagem = data.get("message", "").lower()
    resposta = []

    if numero not in historico_conversas:
        historico_conversas[numero] = []
        historico_conversas[numero].append(f"Cliente: {mensagem}")
        resposta.append({
            "message": "Olá! 👋 Seja bem-vindo! Aqui você tem acesso a *canais de TV, filmes e séries*. 📺🍿\nVamos começar seu teste gratuito?\n\nMe diga qual aparelho você quer usar (ex: TV LG, Roku, Celular, Computador...)."
        })
        return jsonify({"replies": resposta})

    historico_conversas[numero].append(f"Cliente: {mensagem}")

    # Salvar tipo de dispositivo se detectado
    if numero not in dispositivos_detectados:
        tipo = detectar_dispositivo(mensagem)
        if tipo:
            dispositivos_detectados[numero] = tipo
            if tipo == "xcloud":
                resposta.append({"message": "Perfeito! Para sua TV, use o app *Xcloud*. Quando terminar de instalar, me avise dizendo 'instalei' ou 'pronto'."})
                return jsonify({"replies": resposta})
            elif tipo == "xtream":
                resposta.append({"message": "Ótimo! Baixe o app *Xtream IPTV Player* na sua loja de apps. Me avise quando terminar pra eu gerar seu login."})
                return jsonify({"replies": resposta})
            elif tipo == "smarters":
                resposta.append({"message": "Legal! No iPhone ou PC, use o app *Smarters Player Lite*. Assim que instalar, me avise pra te enviar o login."})
                return jsonify({"replies": resposta})
            elif tipo == "qr":
                resposta.append({"message": "Para esse modelo, preciso que me envie o QR Code do app *OTT Player* ou *Duplecast* instalado na TV."})
                return jsonify({"replies": resposta})
            elif tipo == "mac":
                resposta.append({"message": "Por favor, me envie o endereço *MAC* que aparece no app *SmartOne*."})
                return jsonify({"replies": resposta})

    # Cliente disse que instalou
    if any(p in mensagem for p in ["instalei", "baixei", "pronto", "foi", "baixado"]):
        tipo = dispositivos_detectados.get(numero, "xtream")
        webhook = WEBHOOK_XCLOUD if tipo == "xcloud" else WEBHOOK_GERAL
        login = gerar_login(webhook)
        resposta.append({"message": f"Aqui está seu login de teste:\n\n{login}"})
        resposta.append({"message": "⏳ Em breve vou perguntar se deu tudo certo com seu teste. 😉"})
        testes_em_andamento[numero] = []
        agendar_mensagens(numero)
        return jsonify({"replies": resposta})

    # Mensagens programadas (30min e fim do teste)
    if numero in testes_em_andamento and testes_em_andamento[numero]:
        resposta.extend(testes_em_andamento[numero])
        testes_em_andamento[numero] = []
        return jsonify({"replies": resposta})

    # IA normal
    contexto = "\n".join(historico_conversas[numero][-10:])
    prompt = (
        f"Histórico recente com o cliente:\n{contexto}\n\n"
        f"Mensagem mais recente: '{mensagem}'\n\n"
        "Você é um atendente de IPTV que responde de forma natural, simpática e objetiva. "
        "Use linguagem clara e entenda o que o cliente quer sem depender de palavras exatas. "
        "Se o cliente disser qual aparelho tem, indique o app correto:\n\n"
        "- TV Roku, LG, Samsung, Philco: indique *Xcloud*\n"
        "- Android, TV Box, Celular, Fire Stick: indique *Xtream IPTV Player*\n"
        "- iPhone ou computador: indique *Smarters Player Lite*\n"
        "- Philips ou AOC: indique *OTT Player* ou *Duplecast* (peça o QR)\n"
        "- Se usar SmartOne, peça o MAC\n\n"
        "Se o cliente perguntar o que é IPTV, explique de forma simples.\n"
        "Não diga 'colar o login', diga 'digitar o login'.\n"
        "Se o cliente enviar algo confuso, diga que um atendente humano vai verificar.\n\n"
        "Responda com o texto exato para o WhatsApp."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        texto = response.choices[0].message.content
        historico_conversas[numero].append(f"IA: {texto}")
        resposta.append({"message": texto})
    except Exception as e:
        resposta.append({"message": f"⚠️ Ocorreu um erro: {str(e)}"})

    return jsonify({"replies": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
