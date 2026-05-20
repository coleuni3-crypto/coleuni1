import random
from rag.vector_store import search_vectors
from services.student_service import get_weak_topics


# =====================================================
# 🧠 AI-POWERED FLASHCARDS ENGINE (v2)
# =====================================================
def generate_flashcards(institution_id: str, topic: str, limit: int = 10):

    results = search_vectors(institution_id, topic, top_k=20) or []

    flashcards = []

    for r in results:

        content = (r.get("content") or "").strip()

        if len(content) < 50:
            continue

        flashcards.append({
            "question": f"What is the key idea of {topic}?",
            "answer": content,

            # =================================================
            # 🧠 SIMPLIFIED LEARNING LAYER (EXPLANATION BOOST)
            # =================================================
            "simple_explanation": {
                "short": content[:200],
                "analogy": "Think of this concept as a building block in your understanding of the topic."
            },

            # =================================================
            # 📊 METADATA LAYER (FOR ANALYTICS + UI)
            # =================================================
            "difficulty": _estimate_difficulty(content),
            "source_score": r.get("score", 0.5),
            "video_url": r.get("video_url"),
            "timestamp": r.get("start_time")
        })

    random.shuffle(flashcards)

    return {
        "success": True,
        "engine": "flashcard_engine_v2",
        "topic": topic,
        "total_cards": len(flashcards),
        "flashcards": flashcards[:limit]
    }


# =====================================================
# 📅 SMART REVISION PLAN (v2 UPGRADED)
# =====================================================
def revision_plan(institution_id: str, student_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id) or []
    weak_set = {w["topic"] for w in weak_topics if isinstance(w, dict)}

    plan = []

    for t in topics:

        results = search_vectors(institution_id, t, top_k=5) or []

        # =================================================
        # 🧠 INTELLIGENT IMPORTANCE SCORING ENGINE
        # =================================================
        base_score = 0

        for r in results:
            score = r.get("score", 0.5)

            # inverted relevance scoring (higher = more important)
            base_score += (1 - score)

        # weak topic boost
        if t in weak_set:
            base_score *= 1.7

        # normalize session time
        minutes = max(10, min(60, int(base_score * 40)))

        plan.append({
            "topic": t,
            "importance_score": round(base_score, 2),
            "recommended_revision_time_minutes": minutes,
            "strategy": _get_revision_strategy(t, weak_set)
        })

    plan.sort(key=lambda x: x["importance_score"], reverse=True)

    return {
        "success": True,
        "engine": "revision_engine_v2",
        "daily_revision_plan": plan,
        "weak_topics_used": list(weak_set)
    }


# =====================================================
# 🧠 SMART STUDY SESSION BUILDER (v2)
# =====================================================
def build_study_session(institution_id: str, student_id: str, topic: str):

    flashcards = generate_flashcards(institution_id, topic, limit=5)

    weak_topics = get_weak_topics(student_id, institution_id) or []
    weak_set = {w["topic"] for w in weak_topics if isinstance(w, dict)}

    is_weak = topic in weak_set

    return {
        "success": True,
        "engine": "study_session_builder_v2",
        "topic": topic,
        "is_weak_topic": is_weak,

        # =================================================
        # 🧠 ADAPTIVE LEARNING FLOW
        # =================================================
        "study_flow": [
            "1. Understand concept (AI explanation)",
            "2. Study flashcards",
            "3. Answer recall questions",
            "4. Review mistakes",
            "5. Repeat until mastery"
        ],

        "flashcards": flashcards["flashcards"],

        "focus_mode": "HIGH INTENSITY" if is_weak else "NORMAL"
    }


# =====================================================
# 🧠 HELPER: DIFFICULTY ESTIMATOR (NEW AI LAYER)
# =====================================================
def _estimate_difficulty(text: str):

    text = text.lower()

    hard_signals = ["complex", "advanced", "theory", "derive", "prove"]
    easy_signals = ["basic", "simple", "definition", "introduction"]

    hard_score = sum(1 for w in hard_signals if w in text)
    easy_score = sum(1 for w in easy_signals if w in text)

    if hard_score > easy_score:
        return "hard"

    if easy_score > hard_score:
        return "easy"

    return "medium"


# =====================================================
# 🧠 HELPER: REVISION STRATEGY ENGINE
# =====================================================
def _get_revision_strategy(topic: str, weak_set: set):

    if topic in weak_set:
        return "Focus heavily (weak topic + active recall + repetition)"

    return "Normal revision (review + practice questions)"