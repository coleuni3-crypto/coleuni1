from services.student_service import (
    save_student_interaction,
    get_weak_topics
)

from services.revision_service import generate_flashcards
from rag.vector_store import search_vectors


# =====================================================
# 🔁 CORE LEARNING LOOP ENGINE
# =====================================================
def process_learning_event(student_id: str, institution_id: str, query: str, ai_response: str):

    # =================================================
    # 1. SAVE INTERACTION TO MEMORY
    # =================================================
    save_student_interaction(
        student_id,
        institution_id,
        f"Q: {query} | A: {ai_response}"
    )

    # =================================================
    # 2. DETECT WEAK AREAS
    # =================================================
    weak_topics = get_weak_topics(student_id, institution_id)

    # =================================================
    # 3. AUTO-EXTRACT TOPIC FROM QUERY (SIMPLE VERSION)
    # =================================================
    topic = extract_topic(query)

    # =================================================
    # 4. GENERATE FLASHCARDS IF TOPIC IS IMPORTANT
    # =================================================
    flashcards = None

    if topic:
        flashcards = generate_flashcards(institution_id, topic, limit=3)

    # =================================================
    # 5. RETURN LEARNING INSIGHT
    # =================================================
    return {
        "saved": True,
        "detected_topic": topic,
        "weak_topics": weak_topics,
        "flashcards_generated": bool(flashcards),
        "flashcards": flashcards
    }


# =====================================================
# 🧠 SIMPLE TOPIC EXTRACTION (LIGHTWEIGHT VERSION)
# =====================================================
def extract_topic(text: str):

    keywords = [
        "math", "algebra", "physics", "chemistry",
        "biology", "history", "economics", "grammar",
        "programming", "sql", "database"
    ]

    text_lower = text.lower()

    for k in keywords:
        if k in text_lower:
            return k

    return "general"