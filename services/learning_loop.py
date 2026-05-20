from services.student_service import (
    save_student_interaction,
    get_weak_topics
)

from services.revision_service import generate_flashcards
from rag.vector_store import search_vectors


# =====================================================
# 🔁 CORE LEARNING LOOP ENGINE (COLEUNI v3)
# =====================================================
def process_learning_event(student_id: str, institution_id: str, query: str, ai_response: str):

    try:

        # =================================================
        # 1. SAVE INTERACTION TO MEMORY (CLEAN FORMAT)
        # =================================================
        save_student_interaction(
            student_id,
            institution_id,
            {
                "query": query,
                "response": ai_response
            }
        )

        # =================================================
        # 2. GET WEAK AREAS (PERSONALIZATION SIGNAL)
        # =================================================
        weak_topics = get_weak_topics(student_id, institution_id) or []

        weak_set = set(weak_topics)

        # =================================================
        # 3. SMART TOPIC EXTRACTION (IMPROVED v3)
        # =================================================
        topic = extract_topic(query, ai_response)

        # =================================================
        # 4. RAG CONTEXT ENHANCEMENT (FUTURE AI POWER)
        # =================================================
        context_chunks = search_vectors(institution_id, query) or []

        context_score = len(context_chunks)

        # =================================================
        # 5. AUTO FLASHCARD GENERATION (INTELLIGENT TRIGGER)
        # =================================================
        flashcards = None

        if topic and topic != "general" and context_score > 0:

            flashcards = generate_flashcards(
                institution_id,
                topic,
                limit=5
            )

        # =================================================
        # 6. WEAK TOPIC TRIGGER FLAG
        # =================================================
        is_weak = topic in weak_set

        # =================================================
        # 7. RETURN LEARNING INSIGHT OBJECT
        # =================================================
        return {
            "success": True,
            "engine": "learning-loop-v3",
            "data": {
                "saved": True,
                "detected_topic": topic,
                "is_weak_topic": is_weak,
                "weak_topics": weak_topics,
                "rag_context_found": context_score > 0,
                "flashcards_generated": bool(flashcards),
                "flashcards": flashcards
            }
        }

    except Exception as e:
        return {
            "success": False,
            "engine": "learning-loop-v3",
            "error": str(e)
        }


# =====================================================
# 🧠 SMART TOPIC EXTRACTION ENGINE (UPGRADED)
# =====================================================
def extract_topic(query: str, ai_response: str = ""):

    text = f"{query} {ai_response}".lower()

    # =================================================
    # 🎯 CORE SUBJECT INTELLIGENCE MAP
    # =================================================
    subject_map = {
        "mathematics": ["math", "algebra", "geometry", "calculus", "equation"],
        "science": ["physics", "chemistry", "biology", "experiment"],
        "programming": ["python", "sql", "database", "code", "function"],
        "economics": ["economics", "supply", "demand", "market"],
        "language": ["grammar", "essay", "writing", "comprehension"],
        "history": ["history", "war", "independence", "civilization"]
    }

    # =================================================
    # 🔍 MATCH SCORING (INTELLIGENT DETECTION)
    # =================================================
    best_match = "general"
    best_score = 0

    for subject, keywords in subject_map.items():

        score = sum(1 for k in keywords if k in text)

        if score > best_score:
            best_score = score
            best_match = subject

    return best_match