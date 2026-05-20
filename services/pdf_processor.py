from pypdf import PdfReader
from io import BytesIO
import re


# =====================================================
# 🧹 TEXT CLEANING PIPELINE
# =====================================================
def _clean_text(text: str) -> str:

    if not text:
        return ""

    # remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # remove weird PDF artifacts
    text = text.replace("\x00", " ")

    return text.strip()


# =====================================================
# 📄 EXTRACT TEXT FROM PDF (COLEUNI v2)
# =====================================================
def extract_text_from_pdf(file_bytes: bytes):

    if not file_bytes:
        return {
            "success": False,
            "error": "Empty file provided",
            "text": ""
        }

    try:
        pdf = PdfReader(BytesIO(file_bytes))

        pages_text = []
        full_text = ""

        # =================================================
        # 📚 PAGE-BY-PAGE EXTRACTION
        # =================================================
        for i, page in enumerate(pdf.pages):

            text = page.extract_text()

            if text:
                cleaned = _clean_text(text)

                pages_text.append({
                    "page": i + 1,
                    "text": cleaned
                })

                full_text += cleaned + "\n"

        full_text = full_text.strip()

        # =================================================
        # 📊 RETURN STRUCTURED OUTPUT
        # =================================================
        return {
            "success": True,
            "engine": "pdf_extractor_v2",
            "data": {
                "total_pages": len(pdf.pages),
                "text": full_text,
                "pages": pages_text
            }
        }

    except Exception as e:
        print("[PDF EXTRACTION ERROR]", str(e))

        return {
            "success": False,
            "engine": "pdf_extractor_v2",
            "error": str(e),
            "data": {
                "text": ""
            }
        }