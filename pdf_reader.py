import pdfplumber
import re

def leer_pdf_fel(pdf_path):
    texto = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += t + "\n"

    if not texto.strip():
        raise ValueError("El PDF no contiene texto legible")

    uuid = re.search(
        r"[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}",
        texto
    )

    total = re.search(
        r"TOTALES:\s*[\d\.]+\s*([\d\.]+)",
        texto
    )

    nit_emisor = re.search(
        r"Nit Emisor:\s*([\d]+)",
        texto,
        re.IGNORECASE
    )

    receptor = re.search(
        r"NIT Receptor:\s*([\d]+)",
        texto,
        re.IGNORECASE
    )

    empresa = texto.split("\n")[1].strip()

    if not uuid or not total or not nit_emisor:
        raise ValueError("No se pudieron extraer los datos del PDF SAT")

    return {
        "empresa": empresa,
        "nit_emisor": nit_emisor.group(1),
        "id_receptor": receptor.group(1) if receptor else "CF",
        "total": total.group(1),
        "uuid": uuid.group(0)
    }
