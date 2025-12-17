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

    # UUID SAT
    uuid_match = re.search(
        r"[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}",
        texto
    )

    # TOTAL SAT (TOTALES: 0.00 750.00)
    total_match = re.search(
        r"TOTALES:\s*[\d\.]+\s*([\d\.]+)",
        texto
    )

    # NIT Emisor
    nit_match = re.search(
        r"Nit Emisor:\s*([\d]+)",
        texto,
        re.IGNORECASE
    )

    # Empresa (primera línea útil)
    empresa = texto.split("\n")[1].strip()

    if not uuid_match or not total_match or not nit_match:
        raise ValueError(
            "No se pudieron extraer los datos del PDF SAT.\n"
            f"UUID: {bool(uuid_match)}\n"
            f"TOTAL: {bool(total_match)}\n"
            f"NIT: {bool(nit_match)}"
        )

    return {
        "empresa": empresa,
        "nit": nit_match.group(1),
        "total": total_match.group(1),
        "uuid": uuid_match.group(0)
    }
