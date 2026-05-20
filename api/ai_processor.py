import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.supabase_http import insert


# =====================================================
# 🧠 TEXT CLEANER (ROBUST + SAFE)
# =====================================================
def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?-]", "", text)
    return text.strip()


# =====================================================
# ✂️ SENTENCE EXTRACTOR (SMART SPLITTING)
# =====================================================
def extract_sentences(text: str, limit: int = 12) -> List[str]:
    sentences = re.split(r"[.!?]", text)
    cleaned = []

    for s in sentences:
        s = s.strip()
        if len(s) > 25:
            cleaned.append(s)

        if len(cleaned) >= limit:
            break

    return cleaned


# =====================================================
# 🧠 FLASHCARD ENGINE (IMPROVED LOGIC)
# =====================================================
def generate_flashcards(sentences: List[str]) -> List[Dict[str, str]]:
    flashcards = []

    for s in sentences:
        flashcards.append({
            "question": f"What does this concept mean?",
            "context": s[:120],
            "answer": s
        })

    return flashcards


# =====================================================
# ❓ QUIZ ENGINE (MULTI-COMPREHENSION STYLE)
# =====================================================
def generate_quiz(sentences: List[str]) -> List[Dict[str, str]]:
    quiz = []

    for s in sentences:
        quiz.append({
            "question": f"Explain the following idea:",
            "statement": s,
            "expected_answer": s
        })

    return quiz


# =====================================================
# 📊 KEY CONCEPTS EXTRACTOR (LIGHTWEIGHT NLP STYLE)
# =====================================================
def extract_key_concepts(text: str) -> List[str]:
    words = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    return list(set(words))[:10]


# =====================================================
# 🧠 DIFFICULTY ESTIMATOR
# =====================================================
def estimate_difficulty(text: str) -> str:
    length = len(text)

    if length < 500:
        return "easy"
    elif length < 2000:
        return "medium"
    return "hard"


# =====================================================
# 🧠 MAIN AI PROCESSING PIPELINE (V5 CORE)
# =====================================================
def process_learning_material(
    material_id: str,
    text: str,
    course: str,
    title: Optional[str] = None
) -> Dict[str, Any]:

    try:
        cleaned_text = clean_text(text)
        sentences = extract_sentences(cleaned_text)

        flashcards = generate_flashcards(sentences)
        quiz = generate_quiz(sentences)
        key_concepts = extract_key_concepts(cleaned_text)
        difficulty = estimate_difficulty(cleaned_text)

        summary = " ".join(sentences[:3]) if sentences else cleaned_text[:200]

        # =================================================
        # 💾 SAVE TO DATABASE (AI CONTENT LAYER)
        # =================================================
        record = insert("ai_learning_content", {
            "material_id": material_id,
            "course": course,
            "title": title or "",
            "summary": summary,
            "key_concepts": key_concepts,
            "flashcards": flashcards,
            "quiz": quiz,
            "difficulty": difficulty,
            "raw_text": cleaned_text,
            "created_at": datetime.utcnow().isoformat()
        })

        return {
            "success": True,
            "engine": "coleuni-ai-processor-v5",
            "material_id": material_id,
            "difficulty": difficulty,
            "flashcards_count": len(flashcards),
            "quiz_count": len(quiz),
            "key_concepts_count": len(key_concepts),
            "data": record
        }

    except Exception as e:
        print("[AI PROCESSING ERROR]", str(e))
        return {
            "success": False,
            "error": str(e),
            "engine": "ai-processor-v5"
        }