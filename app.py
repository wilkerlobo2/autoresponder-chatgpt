from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
import os

app = FastAPI()

# Inicializa o cliente da OpenAI com a chave da variável de ambiente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    sender = data.get("sender")

    if not message or not sender:
        return JSONResponse(status_code=400, content={"error": "Mensagem e remetente são obrigatórios."})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    
    except Exception as e:
        # Mostra o erro detalhado no retorno para facilitar o debug
        return JSONResponse(status_code=500, content={"error": str(e)})
