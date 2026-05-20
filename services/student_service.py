from core.supabase_http import select, insert
from datetime import datetime
from collections import defaultdict


# =====================================================
# 🔐 SAFE UTIL
# =====================================================
def _safe_list(data):
    return data if isinstance(data, list) else []


# =====================================================
# 🧠 STUDENT MEMORY ENGINE (V5 AI PERSONALIZATION CORE)
# =====================================================
def get_student_memory(student_id: str, institution_id: str, limit: int = 10):

    data = select("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    # sort latest first
    data = sorted(
        data,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )[:limit]

    if not data:
        return {
            "summary": "New learner - no interaction history",
            "interactions": [],
            "memory_strength": 0.0
        }

    interactions = [
        d.get("content", "")
        for d in data
        if d.get("content")
    ]

    return {
        "summary": f"{len(interactions)} learning interactions recorded",
        "interactions": interactions,
        "memory_strength": round(min(len(interactions) / 20, 1.0), 2)
    }


# =====================================================
# 📉 WEAK TOPICS ENGINE (V5 AI RISK MODEL)
# =====================================================
def get_weak_topics(student_id: str, institution_id: str):

    data = select("student_performance", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    topic_scores = defaultdict(list)

    for d in data:
        topic = d.get("topic")
        score = d.get("score")

        if topic is not None and score is not None:
            topic_scores[topic].append(score)

    weak_topics = []

    for topic, scores in topic_scores.items():

        if not scores:
            continue

        avg = sum(scores) / len(scores)

        risk_level = (
            "high" if avg < 40 else
            "medium" if avg < 50 else
            "low"
        )

        if avg < 50:
            weak_topics.append({
                "topic": topic,
                "average_score": round(avg, 2),
                "risk_level": risk_level,
                "status": "weak"
            })

    return sorted(weak_topics, key=lambda x: x["average_score"])


# =====================================================
# 🧾 SAVE STUDENT INTERACTION (AI MEMORY CORE)
# =====================================================
def save_student_interaction(
    student_id: str,
    institution_id: str,
    content: str,
    tag: str = "chat"
):

    if not content or len(content.strip()) < 2:
        return None

    return insert("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id,
        "content": content.strip(),
        "tag": tag,
        "importance": 1,
        "created_at": datetime.utcnow().isoformat()
    })


# =====================================================
# 📊 STUDENT PERFORMANCE SUMMARY (V5 ANALYTICS CORE)
# =====================================================
def get_student_summary(student_id: str, institution_id: str):

    data = select("student_performance", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    scores = [
        d.get("score", 0)
        for d in data
        if d.get("score") is not None
    ]

    if not scores:
        return {
            "total_tests": 0,
            "average_score": 0,
            "performance_level": "no_data"
        }

    avg = sum(scores) / len(scores)

    return {
        "total_tests": len(scores),
        "average_score": round(avg, 2),
        "performance_level": (
            "excellent" if avg >= 75 else
            "average" if avg >= 50 else
            "at-risk"
        )
    }


# =====================================================
# 🎯 LEARNING INSIGHT ENGINE (AI DECISION LAYER V5)
# =====================================================
def get_learning_insight(student_id: str, institution_id: str):

    summary = get_student_summary(student_id, institution_id)
    weak = get_weak_topics(student_id, institution_id)

    if weak:
        top_risk = weak[0]["topic"]
        recommendation = f"Focus deeply on '{top_risk}' to improve exam performance"
    else:
        recommendation = "Strong progress — maintain revision consistency"

    return {
        "performance": summary,
        "weak_topics": weak,
        "recommendation": recommendation,
        "insight_level": (
            "high-risk" if summary["average_score"] < 50 else "stable"
        ),
        "ai_ready": True
    }