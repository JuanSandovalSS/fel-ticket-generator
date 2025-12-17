import pdfplumber
import re
from PIL import Image, ImageDraw, ImageFont
import qrcode

ANCHO_MM = 80
DPI = 203
ANCHO_PX = int(ANCHO_MM / 25.4 * DPI)
FONT = ImageFont.load_default()

def extraer_datos(pdf_path):
    texto = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    uuid = re.search(r"[A-F0-9\-]{36}", texto).group()
    total = re.search(r"Total\s*Q\s*([\d\.]+)", texto).group(1)
    nit = re.search(r"NIT[:\s]*([\d\-]+)", texto).group(1)

    empresa = texto.split("\n")[0]

    return {
        "empresa": empresa,
        "nit": nit,
        "total": total,
        "uuid": uuid
    }

def generar_ticket(data, output="ticket.png"):
    img = Image.new("RGB", (ANCHO_PX, 600), "white")
    d = ImageDraw.Draw(img)
    y = 10

    def center(text):
        nonlocal y
        w, h = d.textsize(text, FONT)
        d.text(((ANCHO_PX-w)//2, y), text, fill="black", font=FONT)
        y += h + 5

    center(data["empresa"])
    center(f"NIT: {data['nit']}")
    y += 10
    center(f"TOTAL Q {data['total']}")
    y += 15

    url = (
        "https://felpub.c.sat.gob.gt/verificador-web/"
        "publico/vistas/verificacionDte.jsf?uuid="
        + data["uuid"]
    )

    qr = qrcode.make(url).resize((200, 200))
    img.paste(qr, ((ANCHO_PX-200)//2, y))
    y += 210

    center("Gracias por su compra")
    img.crop((0, 0, ANCHO_PX, y+10)).save(output)

    print("✅ Ticket generado:", output)

if __name__ == "__main__":
    datos = extraer_datos("factura.pdf")
    generar_ticket(datos)
