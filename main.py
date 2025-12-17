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
    receptor = xml.find(f".//{{{dte}}}Receptor")

    total = xml.find(f".//{{{dte}}}GranTotal").text
    uuid = xml.find(f".//{{{dte}}}NumeroAutorizacion").text

    empresa = emisor.get("NombreComercial") or emisor.get("Nombre")
    nit_emisor = emisor.get("NITEmisor")

    id_receptor = (
        receptor.get("IDReceptor") or
        receptor.get("NITReceptor") or
        "CF"
    )

    return {
        "empresa": empresa,
        "nit_emisor": nit_emisor,
        "id_receptor": id_receptor,
        "total": total,
        "uuid": uuid
    }

# =============================
# GENERADOR DE TICKET PNG
# =============================
def generar_ticket(data, output="ticket.png"):
    # ===== CONFIG 58mm =====
    ANCHO_MM = 58
    DPI = 203
    MARGEN = 4
    QR_SIZE = 160

    ANCHO_PX = int(ANCHO_MM / 25.4 * DPI)

    img = Image.new("RGB", (ANCHO_PX, 720), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    y = 8

    def center(text, space=4):
        nonlocal y
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((ANCHO_PX - w) // 2, y), text, fill="black", font=font)
        y += h + space

    def left(text, space=3):
        nonlocal y
        bbox = d.textbbox((0, 0), text, font=font)
        h = bbox[3] - bbox[1]
        d.text((MARGEN, y), text, fill="black", font=font)
        y += h + space

    # ===== NOMBRE COMERCIAL =====
    center("BOUTIQUE DON JUAN", 8)

    # ===== NOMBRE FISCAL =====
    center(data["empresa"], 10)

    # ===== DATOS FISCALES =====
    left(f"NIT Emisor: {data['nit_emisor']}")
    left(f"ID Receptor: {data['id_receptor']}")
    y += 4

    left("No. Autorización:")
    left(data["uuid"])
    y += 8

    # ===== TOTAL =====
    center(f"TOTAL Q {data['total']}", 10)

    # ===== QR SAT =====
    url = (
        "https://felpub.c.sat.gob.gt/verificador-web/"
        "publico/vistas/verificacionDte.jsf?uuid="
        + data["uuid"]
    )

    qr = qrcode.make(url).resize((QR_SIZE, QR_SIZE))
    img.paste(qr, ((ANCHO_PX - QR_SIZE) // 2, y))
    y += QR_SIZE + 10

    center("Gracias por su compra", 6)

    img = img.crop((0, 0, ANCHO_PX, y + 8))
    img.save(output)
