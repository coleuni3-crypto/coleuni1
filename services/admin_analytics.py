from core.supabase_http import select
from collections import defaultdict
from statistics import mean


# =====================================================
# 📊 SYSTEM ANALYTICS (INSTITUTION LEVEL - V5)
# =====================================================
def get_system_analytics(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    if not data:
        return {
            "status": "empty",
            "total_interactions": 0,
            "average_score": 0,
            "weak_topics": [],
            "strong_topics": [],
            "insight": "No learning data yet"
        }

    # =====================================================
    # 📊 BASIC METRICS
    # =====================================================
    scores = [r.get("score") for r in data if isinstance(r.get("score"), (int, float))]
    total_interactions = len(data)
    avg_score = round(mean(scores), 2) if scores else 0

    # =====================================================
    # 🧠 TOPIC INTELLIGENCE ENGINE (IMPROVED)
    # =====================================================
    topic_scores = defaultdict(list)

    for row in data:
        topic = row.get("topic") or "unknown"
        score = row.get("score")

        if isinstance(score, (int, float)):
            topic_scores[topic].append(score)

    topic_analysis = []
    for topic, scores in topic_scores.items():
        if not scores:
            continue

        topic_analysis.append({
            "topic": topic,
            "average_score": round(mean(scores), 2),
            "attempts": len(scores)
        })

    # =====================================================
    # 📉 WEAK / STRONG DETECTION (SMART THRESHOLDS)
    # =====================================================
    weak_topics = sorted(topic_analysis, key=lambda x: x["average_score"])[:5]
    strong_topics = sorted(topic_analysis, key=lambda x: x["average_score"], reverse=True)[:5]

    # =====================================================
    # 🧠 INSIGHT ENGINE (NEW)
    # =====================================================
    insight = "Stable learning performance"

    if avg_score < 40:
        insight = "Critical learning risk detected"
    elif avg_score < 60:
        insight = "Moderate performance - needs improvement"
    elif avg_score > 80:
        insight = "Excellent learning performance"

    return {
        "status": "success",
        "engine": "coleuni-analytics-v5",
        "total_interactions": total_interactions,
        "average_score": avg_score,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "insight": insight
    }


# =====================================================
# 💰 COST ESTIMATION (SAAS MODEL V2)
# =====================================================
def estimate_cost(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    usage = len(data)

    # smarter pricing tiers
    if usage < 100:
        rate = 0.0015
    elif usage < 1000:
        rate = 0.0012
    else:
        rate = 0.001

    cost = usage * rate

    return {
        "status": "success",
        "usage_count": usage,
        "rate_per_request": rate,
        "estimated_cost_usd": round(cost, 4),
        "engine": "coleuni-cost-v2"
    }


# =====================================================
# 🧑‍🎓 TOP STUDENTS (CLEAN RANKING ENGINE)
# =====================================================
def get_top_students(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    if not data:
        return []

    student_scores = defaultdict(list)

    for row in data:
        sid = row.get("student_id")
        score = row.get("score")

        if sid and isinstance(score, (int, float)):
            student_scores[sid].append(score)

    ranked = [
        {
            "student_id": sid,
            "average_score": round(mean(scores), 2),
            "total_attempts": len(scores)
        }
        for sid, scores in student_scores.items()
    ]

    ranked.sort(key=lambda x: x["average_score"], reverse=True)

    return ranked[:10]


# =====================================================
# ⚠️ AT-RISK STUDENTS (SMART DETECTION V2)
# =====================================================
def get_at_risk_students(institution_id: str):

    data = select("student_performance", {
        "institution_id": institution_id
    }) or []

    if not data:
        return []

    student_scores = defaultdict(list)

    for row in data:
        sid = row.get("student_id")
        score = row.get("score")

        if sid and isinstance(score, (int, float)):
            student_scores[sid].append(score)

    at_risk = []

    for sid, scores in student_scores.items():
        avg = mean(scores)

        risk_level = None

        if avg < 40:
            risk_level = "critical"
        elif avg < 55:
            risk_level = "high"
        elif avg < 65:
            risk_level = "medium"

        if risk_level:
            at_risk.append({
                "student_id": sid,
                "average_score": round(avg, 2),
                "risk_level": risk_level,
                "attempts": len(scores)
            })

    return sorted(at_risk, key=lambda x: x["average_score"])