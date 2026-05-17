from services.student_service import get_weak_topics
from rag.vector_store import search_vectors


# =====================================================
# 📊 EXAM PREDICTION ENGINE (AI ANALYTICS CORE)
# =====================================================
def predict_exam_performance(student_id: str, institution_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id)

    weak_set = {w["topic"] for w in weak_topics}

    predictions = []

    for topic in topics:

        results = search_vectors(institution_id, topic, top_k=5)

        avg_score = sum([r.get("score", 0.5) for r in results]) / len(results) if results else 0.5

        # =================================================
        # 🧠 RISK MODEL (SIMPLE BUT EFFECTIVE)
        # =================================================
        weakness_penalty = 0.3 if topic in weak_set else 0

        predicted_score = max(0, min(1, avg_score - weakness_penalty))

        predictions.append({
            "topic": topic,
            "predicted_score": round(predicted_score * 100, 2),
            "risk_level": (
                "HIGH RISK" if predicted_score < 0.4 else
                "MEDIUM RISK" if predicted_score < 0.7 else
                "LOW RISK"
            ),
            "is_weak_topic": topic in weak_set
        })

    # sort worst first
    predictions.sort(key=lambda x: x["predicted_score"])

    return {
        "student_risk_profile": predictions,
        "overall_status": "AT RISK" if any(p["predicted_score"] < 50 for p in predictions) else "OK"
    }