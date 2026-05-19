import fitz  # PyMuPDF


# =========================
# 📄 EXTRACT TEXT FROM FILE
# =========================
def extract_text_from_pdf(file_bytes: bytes):

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    return text


# =========================
# 🧠 AI CONTENT GENERATOR (MVP VERSION)
# =========================
def generate_learning_package(text: str):

    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]

    # =========================
    # 📚 NOTES
    # =========================
    notes = "\n".join(sentences[:12])

    # =========================
    # 🧠 FLASHCARDS
    # =========================
    flashcards = [
        {
            "question": f"What does this mean? ({i+1})",
            "answer": s
        }
        for i, s in enumerate(sentences[:6])
    ]

    # =========================
    # ❓ QUIZ
    # =========================
    quiz = [
        {
            "question": f"Explain: {s[:60]}...",
            "answer": s
        }
        for s in sentences[:5]
    ]

    # =========================
    # 🔊 AUDIO SCRIPT
    # =========================
    audio_text = notes

    return {
        "notes": notes,
        "flashcards": flashcards,
        "quiz": quiz,
        "audio_text": audio_text
    }