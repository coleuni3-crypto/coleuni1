from pypdf import PdfReader
from io import BytesIO


# =====================================================
# 📄 EXTRACT TEXT FROM PDF
# =====================================================
def extract_text_from_pdf(file_bytes: bytes):

    try:
        pdf = PdfReader(BytesIO(file_bytes))

        full_text = ""

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

        return full_text.strip()

    except Exception as e:
        print("[PDF EXTRACTION ERROR]", e)
        return ""