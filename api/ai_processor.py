import re
from core.supabase_http import insert

# =====================================================
# 🧠 SIMPLE AI TEXT PROCESSOR (MVP ENGINE)
# Later upgrade → OpenAI / LLM
# =====================================================

def clean_text(text: str):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================================
# 📚 FLASHCARD GENERATOR
# =====================================================
def generate_flashcards(text: str):
    sentences = text.split(".")
    flashcards = []

    for s in sentences[:10]:
        s = s.strip()
        if len(s) < 20:
            continue

        flashcards.append({
            "question": f"What does this mean: {s[:40]}?",
            "answer": s
        })

    return flashcards


# =====================================================
# ❓ QUIZ GENERATOR
# =====================================================
def generate_quiz(text: str):
    sentences = text.split(".")
    quiz = []

    for s in sentences[:6]:
        s = s.strip()
        if len(s) < 20:
            continue

        quiz.append({
            "question": f"Explain: {s[:40]}...",
            "answer": s
        })

    return quiz


# =====================================================
# 🧠 MAIN AI PROCESSOR PIPELINE
# =====================================================
def process_learning_material(material_id: str, text: str, course: str):

    text = clean_text(text)

    flashcards = generate_flashcards(text)
    quiz = generate_quiz(text)

    result = insert("ai_learning_content", {
        "material_id": material_id,
        "course": course,
        "flashcards": flashcards,
        "quiz": quiz,
        "raw_text": text
    })

    return {
        "success": True,
        "material_id": material_id,
        "flashcards_count": len(flashcards),
        "quiz_count": len(quiz),
        "data": result
    }