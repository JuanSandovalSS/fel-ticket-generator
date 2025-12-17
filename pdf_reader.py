import pdfplumber
import re

def leer_pdf_fel(pdf_path):
    texto = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += t + "\n"

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
