from services.student_service import get_weak_topics
from rag.vector_store import search_vectors


# =====================================================
# 🧠 EXAM PREDICTION ENGINE v2 (COLEUNI AI CORE)
# =====================================================
def predict_exam_performance(student_id: str, institution_id: str, topics: list):

    if not topics:
        return {
            "student_risk_profile": [],
            "overall_status": "NO DATA",
            "risk_score": 0
        }

    # =========================
    # ⚠️ WEAK TOPIC SET (FAST LOOKUP)
    # =========================
    weak_topics_raw = get_weak_topics(student_id, institution_id)
    weak_set = set(weak_topics_raw or [])

    predictions = []
    total_score = 0

    # =========================
    # 🧠 CORE PREDICTION LOOP
    # =========================
    for topic in topics:

        try:
            results = search_vectors(institution_id, topic, top_k=5) or []

            # =========================
            # 📊 VECTOR SCORE NORMALIZATION
            # =========================
            scores = [
                r.get("score", 0.5)
                for r in results
                if isinstance(r, dict)
            ]

            avg_score = sum(scores) / len(scores) if scores else 0.5

            # =========================
            # 📉 WEAKNESS PENALTY MODEL (IMPROVED)
            # =========================
            is_weak = topic in weak_set

            weakness_penalty = 0.25 if is_weak else 0

            # slight confidence boost if many good vectors
            confidence_boost = 0.05 if len(scores) >= 4 else 0

            predicted_score = avg_score - weakness_penalty + confidence_boost

            predicted_score = max(0.0, min(1.0, predicted_score))

            final_score = round(predicted_score * 100, 2)

            total_score += final_score

            # =========================
            # 📊 RISK CLASSIFICATION
            # =========================
            if final_score < 40:
                risk = "HIGH RISK"
            elif final_score < 70:
                risk = "MEDIUM RISK"
            else:
                risk = "LOW RISK"

            predictions.append({
                "topic": topic,
                "predicted_score": final_score,
                "risk_level": risk,
                "is_weak_topic": is_weak,
                "confidence": round(len(scores) / 5, 2)
            })

        except Exception:
            # safe fallback per topic
            predictions.append({
                "topic": topic,
                "predicted_score": 50,
                "risk_level": "UNKNOWN",
                "is_weak_topic": topic in weak_set,
                "confidence": 0
            })

            total_score += 50

    # =========================
    # 📈 OVERALL RISK INDEX
    # =========================
    avg_score = total_score / len(topics)

    if avg_score < 45:
        overall_status = "CRITICAL RISK"
    elif avg_score < 70:
        overall_status = "AT RISK"
    else:
        overall_status = "STABLE"

    # =========================
    # 🧠 FINAL RESPONSE
    # =========================
    return {
        "student_risk_profile": sorted(
            predictions,
            key=lambda x: x["predicted_score"]
        ),
        "overall_status": overall_status,
        "risk_score": round(avg_score, 2),
        "total_topics_analyzed": len(topics),
        "engine": "coleuni-exam-ai-v2"
    }