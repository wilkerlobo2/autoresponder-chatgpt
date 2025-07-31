from flask import Flask, request, jsonify import random import datetime import threading

app = Flask(name)

Lista de números para login de teste

numeros_login = ["221", "225", "500", "555"]

Controle de estados por número

estado_cliente = {}

Planos e pagamento

planos = """ 🌟 Planos Disponíveis:

✅ 1 mês: R$ 26,00 ✅ 2 meses: R$ 47,00 ✅ 3 meses: R$ 68,00 ✅ 6 meses: R$ 129,00 ✅ 1 ano: R$ 185,00

💳 Pagamento via PIX (CNPJ): 00.000.000/0001-00

💼 Pagamento com cartão: https://seulinkdecartao.com """

Função auxiliar para enviar mensagens com atraso

mensagens_pendentes = {}

def agendar_mensagem(numero, mensagem, delay): def enviar(): mensagens_pendentes[numero].append(mensagem) if numero not in mensagens_pendentes: mensagens_pendentes[numero] = [] t = threading.Timer(delay, enviar) t.start()

def verificar_mensagens(numero): if numero in mensagens_pendentes and mensagens_pendentes[numero]: return mensagens_pendentes[numero].pop(0) return None

def gerar_resposta(numero, mensagem): texto = mensagem.lower().strip() estado = estado_cliente.get(numero, {})

if texto.startswith("+"):  # Novo cliente
    estado_cliente[numero] = {"etapa": "inicio"}
    return "Oi! Bem-vindo ✨\nQuer fazer um teste e conhecer nossos canais ao vivo, filmes e séries? Me diz seu dispositivo (ex: Samsung, LG, Roku, Android...) que te oriento com o app ideal."

if any(x in texto for x in ["foto", "imagem", ".jpg", ".png"]):
    return "Recebi sua imagem. Assim que eu analisar, te respondo."

if "audio" in texto:
    return "Recebi o áudio. Vou escutar e já te respondo."

if "android" in texto:
    estado_cliente[numero] = {"etapa": "aguardando_download", "modelo": "android"}
    return "Para Android TV, TV Box ou Toshiba/Vizzion/Vidaa, baixe o app *Xtream IPTV Player* 👉 Quando baixar, me avise para eu te passar o próximo passo."

if "roku" in texto:
    estado_cliente[numero] = {"etapa": "aguardando_download", "modelo": "roku"}
    return "Na Roku, tente primeiro o app *Xcloud (verde e preto)*. Quando instalar, me avisa."

if "samsung" in texto:
    return "Seu modelo é novo ou antigo? Se for novo, usamos o app Xcloud. Se for antigo, te passo o código direto."

if "lg" in texto:
    estado_cliente[numero] = {"etapa": "aguardando_download", "modelo": "lg"}
    return "Recomendo o app *Xcloud*. Se não funcionar, podemos tentar o Duplecast (com QR) ou SmartOne (com MAC). Baixe o Xcloud e me avise.

