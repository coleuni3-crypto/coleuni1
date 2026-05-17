from core.supabase_http import select


# =====================================================
# 📊 SYSTEM ANALYTICS (INSTITUTION LEVEL)
# =====================================================
def get_system_analytics(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    if not data:
        return {
            "total_interactions": 0,
            "average_score": 0,
            "weak_topics": [],
            "strong_topics": []
        }

    total_interactions = len(data)

    scores = [row.get("score", 0) for row in data if row.get("score") is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    # =====================================================
    # TOPIC GROUPING (IN MEMORY - SUPABASE SAFE)
    # =====================================================
    topic_map = {}

    for row in data:
        topic = row.get("topic", "unknown")
        score = row.get("score", 0)

        topic_map.setdefault(topic, []).append(score)

    topic_avg = [
        {
            "topic": topic,
            "score": round(sum(scores) / len(scores), 2)
        }
        for topic, scores in topic_map.items()
        if scores
    ]

    # weak topics (lowest performance)
    weak_topics = sorted(topic_avg, key=lambda x: x["score"])[:5]

    # strong topics (highest performance)
    strong_topics = sorted(topic_avg, key=lambda x: x["score"], reverse=True)[:5]

    return {
        "total_interactions": total_interactions,
        "average_score": round(avg_score, 2),
        "weak_topics": weak_topics,
        "strong_topics": strong_topics
    }


# =====================================================
# 💰 COST ESTIMATION (SAAS USAGE MODEL)
# =====================================================
def estimate_cost(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    usage = len(data)

    cost = usage * 0.002  # AI usage cost model (placeholder)

    return {
        "usage_count": usage,
        "estimated_cost_usd": round(cost, 4)
    }


# =====================================================
# 🧑‍🎓 TOP STUDENTS
# =====================================================
def get_top_students(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    student_map = {}

    for row in data:
        sid = row.get("student_id")
        score = row.get("score", 0)

        if not sid:
            continue

        student_map.setdefault(sid, []).append(score)

    results = [
        {
            "student_id": sid,
            "average_score": round(sum(scores) / len(scores), 2)
        }
        for sid, scores in student_map.items()
    ]

    return sorted(results, key=lambda x: x["average_score"], reverse=True)[:10]


# =====================================================
# ⚠️ AT-RISK STUDENTS
# =====================================================
def get_at_risk_students(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    student_map = {}

    for row in data:
        sid = row.get("student_id")
        score = row.get("score", 0)

        if not sid:
            continue

        student_map.setdefault(sid, []).append(score)

    results = []

    for sid, scores in student_map.items():
        avg = sum(scores) / len(scores)

        if avg < 50:
            results.append({
                "student_id": sid,
                "average_score": round(avg, 2),
                "risk_level": "high" if avg < 40 else "medium"
            })

    return sorted(results, key=lambda x: x["average_score"])