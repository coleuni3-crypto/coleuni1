from core.supabase_http import select, insert
from datetime import datetime


# =====================================================
# 🧠 STUDENT MEMORY (PERSONALIZATION LAYER)
# =====================================================
def get_student_memory(student_id: str, institution_id: str):

    data = select("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    if not data:
        return {
            "summary": "New student - no learning history",
            "interactions": []
        }

    interactions = [
        d.get("content", "")
        for d in data
        if d.get("content")
    ]

    interactions = interactions[-10:]  # last 10 only

    return {
        "summary": f"{len(interactions)} learning interactions",
        "interactions": interactions
    }


# =====================================================
# 📉 WEAK TOPICS DETECTION
# =====================================================
def get_weak_topics(student_id: str, institution_id: str):

    data = select("student_performance", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    if not data:
        return []

    topic_scores = {}

    for d in data:
        topic = d.get("topic")
        score = d.get("score", 0)

        if not topic:
            continue

        topic_scores.setdefault(topic, []).append(score)

    weak_topics = []

    for topic, scores in topic_scores.items():

        if not scores:
            continue

        avg_score = sum(scores) / len(scores)

        if avg_score < 50:
            weak_topics.append({
                "topic": topic,
                "average_score": round(avg_score, 2),
                "status": "weak"
            })

    return sorted(weak_topics, key=lambda x: x["average_score"])


# =====================================================
# 🧾 SAVE STUDENT INTERACTION
# =====================================================
def save_student_interaction(student_id: str, institution_id: str, content: str):

    if not content:
        return None

    return insert("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    })


# =====================================================
# 📊 STUDENT PERFORMANCE SUMMARY
# =====================================================
def get_student_summary(student_id: str, institution_id: str):

    data = select("student_performance", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    if not data:
        return {
            "total_tests": 0,
            "average_score": 0,
            "status": "no_data"
        }

    scores = [d.get("score", 0) for d in data]

    avg = sum(scores) / len(scores) if scores else 0

    return {
        "total_tests": len(scores),
        "average_score": round(avg, 2),
        "status": "active"
    }


# =====================================================
# 🎯 STUDENT INSIGHT ENGINE (AI READY)
# =====================================================
def get_learning_insight(student_id: str, institution_id: str):

    summary = get_student_summary(student_id, institution_id)
    weak = get_weak_topics(student_id, institution_id)

    if weak:
        recommendation = f"Focus on {weak[0]['topic']} to improve performance"
    else:
        recommendation = "Good progress - keep practicing consistently"

    return {
        "performance": summary,
        "weak_topics": weak,
        "recommendation": recommendation
    }