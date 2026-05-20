from services.student_service import get_weak_topics, get_student_summary
from rag.vector_store import search_vectors
from typing import List, Dict, Any
from datetime import datetime


# =====================================================
# 🧠 SAFE VECTOR SCORE NORMALIZER
# =====================================================
def _avg_vector_score(results: List[dict]) -> float:
    """
    Prevents crashes + ensures stable AI scoring
    """
    if not results:
        return 0.5

    scores = [
        float(r.get("score", 0.5))
        for r in results
        if isinstance(r, dict)
    ]

    return sum(scores) / len(scores) if scores else 0.5


# =====================================================
# 🧠 PRIORITY ENGINE (CORE INTELLIGENCE LAYER)
# =====================================================
def _calculate_priority(topic: str, avg_score: float, weak_set: set) -> float:

    priority = 1 - avg_score

    # boost weak topics
    if topic in weak_set:
        priority += 0.35

    # clamp between 0 and 1
    return max(0.0, min(1.0, priority))


# =====================================================
# 🧠 AI STUDY AUTOPILOT ENGINE (V5 CORE)
# =====================================================
def generate_study_plan(student_id: str, institution_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id) or []
    summary = get_student_summary(student_id, institution_id)

    weak_set = {
        w.get("topic")
        for w in weak_topics
        if isinstance(w, dict)
    }

    plan = []

    for topic in topics:

        results = search_vectors(institution_id, topic, top_k=5)
        avg_score = _avg_vector_score(results)

        priority = _calculate_priority(topic, avg_score, weak_set)

        minutes = max(10, int(priority * 75))

        plan.append({
            "topic": topic,
            "priority_score": round(priority, 3),
            "study_time_minutes": minutes,
            "risk_level": (
                "HIGH" if priority > 0.65 else
                "MEDIUM" if priority > 0.35 else
                "LOW"
            ),
            "mode": (
                "INTENSIVE REVIEW"
                if topic in weak_set
                else "STANDARD REVISION"
            ),
            "confidence": round(avg_score, 2)
        })

    plan.sort(key=lambda x: x["priority_score"], reverse=True)

    return {
        "student_summary": summary,
        "generated_at": datetime.utcnow().isoformat(),
        "autopilot_plan": plan,
        "engine": "coleuni-study-autopilot-v5"
    }


# =====================================================
# 📅 DAILY LEARNING SCHEDULE BUILDER (V5)
# =====================================================
def build_daily_schedule(student_id: str, institution_id: str, topics: list):

    study_plan = generate_study_plan(student_id, institution_id, topics)

    schedule = []
    time_slot = 9  # start 9 AM

    for item in study_plan["autopilot_plan"]:

        schedule.append({
            "time": f"{time_slot:02d}:00",
            "topic": item["topic"],
            "activity": item["mode"],
            "duration_minutes": item["study_time_minutes"],
            "priority": item["priority_score"]
        })

        time_slot += 1

        if time_slot > 18:
            break

    return {
        "daily_schedule": schedule,
        "total_sessions": len(schedule),
        "engine": "coleuni-daily-scheduler-v5"
    }


# =====================================================
# 🧠 AUTO EXAM RISK ANALYZER (V5 IMPROVED MODEL)
# =====================================================
def exam_risk_analysis(student_id: str, institution_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id) or []

    weak_set = {
        w.get("topic")
        for w in weak_topics
        if isinstance(w, dict)
    }

    breakdown = []
    total_risk = 0

    for topic in topics:

        results = search_vectors(institution_id, topic, top_k=5)
        avg_score = _avg_vector_score(results)

        # penalty for weak topics
        if topic in weak_set:
            avg_score -= 0.3

        avg_score = max(0.0, min(1.0, avg_score))

        risk = 1 - avg_score
        total_risk += risk

        breakdown.append({
            "topic": topic,
            "score": round(avg_score * 100, 2),
            "risk": round(risk, 2),
            "status": (
                "WEAK"
                if topic in weak_set
                else "OK"
            )
        })

    final_risk = total_risk / len(topics) if topics else 0

    return {
        "risk_score": round(final_risk, 3),
        "risk_level": (
            "HIGH RISK" if final_risk > 0.65 else
            "MEDIUM RISK" if final_risk > 0.35 else
            "LOW RISK"
        ),
        "breakdown": breakdown,
        "engine": "coleuni-exam-risk-v5"
    }