@app.route("/webhook", methods=["POST"])
def responder():
    try:
        data = request.get_data(as_text=True)  # Recebe como texto bruto
        print("DADOS BRUTOS RECEBIDOS:", data)

        json_data = request.get_json(force=True)
        print("DADOS JSON PARSEADOS:", json_data)

        return jsonify({"debug": json_data})
    except Exception as e:
        print("ERRO AO PROCESSAR:", str(e))
        return jsonify({"error": str(e)}), 400
