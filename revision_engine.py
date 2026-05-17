# =====================================================
# REVISION + FLASHCARD ENGINE (COLEUNI AI)
# =====================================================

from vector_store import search_vectors
import random


# =====================================================
# FLASHCARD GENERATION
# =====================================================
def generate_flashcards(institution_id: str, topic: str, limit: int = 10):

    # ✅ FIXED FUNCTION NAME
    results = search_vectors(institution_id, topic, top_k=20)

    if not results:
        return {
            "flashcards": [],
            "message": "No learning material found"
        }

    flashcards = []

    for r in results:

        content = r["content"]

        if len(content) < 40:
            continue

        flashcards.append({
            "question": f"What is the key concept of: {content[:80]}?",
            "answer": content,
            "video_url": r.get("video_url"),
            "timestamp": r.get("start_time"),
            "difficulty": "medium"
        })

    random.shuffle(flashcards)

    return {
        "topic": topic,
        "flashcards": flashcards[:limit]
    }


# =====================================================
# REVISION PLAN (SPACED REPETITION STYLE)
# =====================================================
def revision_plan(institution_id: str, topics: list):

    plan = []

    for t in topics:

        results = search_vectors(institution_id, t, top_k=5)

        importance = sum([1 - r["score"] for r in results]) if results else 0

        plan.append({
            "topic": t,
            "importance_score": round(importance, 2),
            "recommended_revision_time_minutes": max(10, int(importance * 30))
        })

    # sort by importance
    plan.sort(key=lambda x: x["importance_score"], reverse=True)

    return {
        "daily_revision_plan": plan
    }