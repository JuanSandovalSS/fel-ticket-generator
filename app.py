from flask import Flask, request, send_file, render_template
from main import leer_fel, generar_ticket
from pdf_reader import leer_pdf_fel
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["xml"]
        filename = file.filename.lower()

        if filename.endswith(".xml"):
            path = "factura.xml"
            file.save(path)
            data = leer_fel(path)

        elif filename.endswith(".pdf"):
            path = "factura.pdf"
            file.save(path)
            data = leer_pdf_fel(path)

        generar_ticket(data, "ticket.png")

        return send_file("ticket.png", mimetype="image/png")

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)