# =====================================================
# EXAM PREDICTION ENGINE (COLEUNI AI)
# =====================================================

from vector_store import search_vectors


# =====================================================
# EXAM QUESTION GENERATOR
# =====================================================
def generate_exam_questions(institution_id: str, topic: str):

    # Step 1: pull relevant lecture content
    results = search_vectors(institution_id, topic, top_k=10)

    if not results:
        return {
            "questions": [],
            "message": "No lecture data found"
        }

    questions = []
    topics_seen = set()

    for r in results:

        content = r["content"]

        # simple intelligence extraction (you can upgrade later with NLP clustering)
        if len(content) < 30:
            continue

        # avoid duplicates
        key = content[:50]

        if key in topics_seen:
            continue

        topics_seen.add(key)

        # =====================================================
        # GENERATE EXAM QUESTIONS (RULE-BASED VERSION)
        # =====================================================
        questions.append({
            "question": f"Explain and discuss: {content[:120]}...",
            "type": "long_answer",
            "importance_score": round(1 - r["score"], 2),
            "video_hint": r.get("video_url"),
            "timestamp": r.get("start_time")
        })

    # sort by importance
    questions = sorted(
        questions,
        key=lambda x: x["importance_score"],
        reverse=True
    )

    return {
        "topic": topic,
        "predicted_questions": questions[:10]
    }