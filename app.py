from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai
import os

app = FastAPI()

# Define a chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    sender = data.get("sender")

    if not message or not sender:
        return JSONResponse(status_code=400, content={"error": "Mensagem ou remetente ausente."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return {"reply": reply}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
