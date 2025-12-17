from PIL import Image, ImageDraw, ImageFont
import qrcode
from lxml import etree

# =============================
# LECTOR XML FEL
# =============================
def leer_fel(xml_path):
    xml = etree.parse(xml_path)
    root = xml.getroot()

    ns = root.nsmap
    dte = list(ns.values())[0]

    emisor = xml.find(f".//{{{dte}}}Emisor")
    total = xml.find(f".//{{{dte}}}GranTotal").text
    uuid = xml.find(f".//{{{dte}}}NumeroAutorizacion").text

    empresa = emisor.get("NombreComercial") or emisor.get("Nombre")
    nit = emisor.get("NITEmisor")

    return {
        "empresa": empresa,
        "nit": nit,
        "total": total,
        "uuid": uuid
    }

# =============================
# GENERADOR DE TICKET PNG
# =============================
def generar_ticket(data, output="ticket.png"):
    ANCHO_MM = 80
    DPI = 203
    ANCHO_PX = int(ANCHO_MM / 25.4 * DPI)

    img = Image.new("RGB", (ANCHO_PX, 600), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    y = 10

    def center(text):
        nonlocal y
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((ANCHO_PX - w) // 2, y), text, fill="black", font=font)
        y += h + 6

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
    img.paste(qr, ((ANCHO_PX - 200) // 2, y))
    y += 210

    center("Gracias por su compra")

    img = img.crop((0, 0, ANCHO_PX, y + 10))
    img.save(output)
