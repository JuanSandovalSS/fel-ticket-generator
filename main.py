from lxml import etree
from PIL import Image, ImageDraw, ImageFont
import qrcode
import sys

# =============================
# CONFIGURACIÓN
# =============================
ANCHO_MM = 80
DPI = 203  # impresoras térmicas
ANCHO_PX = int(ANCHO_MM / 25.4 * DPI)

FUENTE = ImageFont.load_default()

# =============================
# LEER XML FEL
# =============================
def leer_fel(xml_path):
    ns = {'dte': 'http://www.sat.gob.gt/dte/fel/0.2.0'}
    xml = etree.parse(xml_path)

    emisor = xml.find('.//dte:Emisor', ns)
    total = xml.find('.//dte:GranTotal', ns).text
    uuid = xml.find('.//dte:NumeroAutorizacion', ns).text

    return {
        "empresa": emisor.get("NombreComercial"),
        "nit": emisor.get("NITEmisor"),
        "total": total,
        "uuid": uuid
    }

# =============================
# GENERAR TICKET
# =============================
def generar_ticket(data, output="ticket.png"):
    alto_px = 600
    img = Image.new("RGB", (ANCHO_PX, alto_px), "white")
    d = ImageDraw.Draw(img)

    y = 10
    centro = ANCHO_PX // 2

    def texto(t, bold=False):
        nonlocal y
        w, h = d.textsize(t, font=FUENTE)
        d.text(((ANCHO_PX - w)//2, y), t, fill="black", font=FUENTE)
        y += h + 5

    texto(data["empresa"])
    texto(f"NIT: {data['nit']}")
    y += 10
    texto(f"TOTAL: Q {data['total']}")
    y += 15

    # QR SAT
    url = (
        "https://felpub.c.sat.gob.gt/verificador-web/"
        "publico/vistas/verificacionDte.jsf?uuid="
        + data["uuid"]
    )

    qr = qrcode.make(url).resize((200, 200))
    img.paste(qr, (centro - 100, y))
    y += 210

    texto("Gracias por su compra")

    img = img.crop((0, 0, ANCHO_PX, y + 10))
    img.save(output)
    print(f"✅ Ticket generado: {output}")

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py factura.xml")
        sys.exit(1)

    datos = leer_fel(sys.argv[1])
    generar_ticket(datos)
