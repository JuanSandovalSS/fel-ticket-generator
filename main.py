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

    img = Image.new("RGB", (ANCHO_PX, 800), "white")
    d = ImageDraw.Draw(img)

    # ===== FUENTES =====
    BASE = os.path.dirname(__file__)
    font_store = ImageFont.truetype(f"{BASE}/fonts/DejaVuSans-Bold.ttf", 24)
    font_company = ImageFont.truetype(f"{BASE}/fonts/DejaVuSans-Bold.ttf", 16)
    font_data = ImageFont.truetype(f"{BASE}/fonts/DejaVuSans-Bold.ttf", 15)
    font_total = ImageFont.truetype(f"{BASE}/fonts/DejaVuSans-Bold.ttf", 28)
    font_footer = ImageFont.truetype(f"{BASE}/fonts/DejaVuSans-Bold.ttf", 14)

    y = 10

    def center(text, font, space=6):
        nonlocal y
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((ANCHO_PX - w) // 2, y), text, fill="black", font=font)
        y += h + space

    def left(text, font, space=4):
        nonlocal y
        bbox = d.textbbox((0, 0), text, font=font)
        h = bbox[3] - bbox[1]
        d.text((MARGEN, y), text, fill="black", font=font)
        y += h + space

    # ===== ENCABEZADO =====
    center("BOUTIQUE DON JUAN", font_store, 10)
    center(data["empresa"], font_company, 12)

    # ===== DATOS FISCALES =====
    left(f"NIT Emisor: {data['nit_emisor']}", font_data)
    left(f"ID Receptor: {data['id_receptor']}", font_data)
    left("No. Autorización:", font_data)
    left(data["uuid"], font_data, 8)

    # ===== TOTAL =====
    center(f"TOTAL Q {data['total']}", font_total, 14)

    # ===== QR =====
    url = (
        "https://felpub.c.sat.gob.gt/verificador-web/"
        "publico/vistas/verificacionDte.jsf?uuid="
        + data["uuid"]
    )

    qr = qrcode.make(url).resize((QR_SIZE, QR_SIZE))
    img.paste(qr, ((ANCHO_PX - QR_SIZE) // 2, y))
    y += QR_SIZE + 12

    center("Gracias por su compra", font_footer, 8)

    img = img.crop((0, 0, ANCHO_PX, y + 10))
    img.save(output)
