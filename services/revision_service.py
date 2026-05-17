import random
from rag.vector_store import search_vectors
from services.student_service import get_weak_topics


# =====================================================
# 🧠 AI-POWERED FLASHCARDS (EXPLAINED VERSION)
# =====================================================
def generate_flashcards(institution_id: str, topic: str, limit: int = 10):

    results = search_vectors(institution_id, topic, top_k=20)

    flashcards = []

    for r in results:

        content = r.get("content", "").strip()

        if len(content) < 40:
            continue

        # =================================================
        # 🧠 BREAK CONTENT INTO SIMPLE TEACHING FORMAT
        # =================================================
        flashcards.append({
            "question": f"What is the key idea of this concept?",
            "answer": content,

            # NEW: AI EXPLANATION LAYER
            "simple_explanation": f"""
In simple terms:
{content[:200]}

Think of it like this:
This concept is important because it helps you understand the topic step by step.
""",

            "video_url": r.get("video_url"),
            "timestamp": r.get("start_time"),
            "difficulty": "medium"
        })

    random.shuffle(flashcards)

    return {
        "topic": topic,
        "total_cards": len(flashcards),
        "flashcards": flashcards[:limit]
    }


# =====================================================
# 📅 SMART REVISION PLAN (ADAPTIVE)
# =====================================================
def revision_plan(institution_id: str, student_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id)

    weak_topic_names = {w["topic"] for w in weak_topics}

    plan = []

    for t in topics:

        results = search_vectors(institution_id, t, top_k=5)

        # =================================================
        # 🧠 INTELLIGENT IMPORTANCE SCORING
        # =================================================
        base_score = sum([1 - r.get("score", 0.5) for r in results]) if results else 0

        # boost weak topics
        if t in weak_topic_names:
            base_score *= 1.5

        minutes = max(10, int(base_score * 30))

        plan.append({
            "topic": t,
            "importance_score": round(base_score, 2),
            "recommended_revision_time_minutes": minutes,

            # NEW: STRATEGY LAYER
            "strategy": (
                "Focus heavily (weak topic)"
                if t in weak_topic_names
                else "Normal revision"
            )
        })

    plan.sort(key=lambda x: x["importance_score"], reverse=True)

    return {
        "daily_revision_plan": plan,
        "weak_topics_used": list(weak_topic_names)
    }


# =====================================================
# 🧠 SMART STUDY SESSION BUILDER
# =====================================================
def build_study_session(institution_id: str, student_id: str, topic: str):

    flashcards = generate_flashcards(institution_id, topic, limit=5)

    weak_topics = get_weak_topics(student_id, institution_id)

    is_weak = any(w["topic"] == topic for w in weak_topics)

    return {
        "topic": topic,
        "is_weak_topic": is_weak,

        "study_flow": [
            "1. Read explanation",
            "2. Answer flashcard",
            "3. Review mistake",
            "4. Repeat until mastery"
        ],

        "flashcards": flashcards["flashcards"],

        "focus_mode": "HIGH INTENSITY" if is_weak else "NORMAL"
    }