from services.student_service import get_weak_topics, get_student_summary
from rag.vector_store import search_vectors


# =====================================================
# 🧠 AI STUDY AUTOPILOT ENGINE
# =====================================================
def generate_study_plan(student_id: str, institution_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id)
    summary = get_student_summary(student_id, institution_id)

    weak_set = {w["topic"] for w in weak_topics}

    plan = []

    for topic in topics:

        results = search_vectors(institution_id, topic, top_k=5)

        avg_score = sum([r.get("score", 0.5) for r in results]) / len(results) if results else 0.5

        # =================================================
        # 🧠 PRIORITY ENGINE
        # =================================================
        priority = 1 - avg_score

        if topic in weak_set:
            priority += 0.3

        # =================================================
        # ⏱ TIME ALLOCATION ENGINE
        # =================================================
        minutes = max(10, int(priority * 60))

        plan.append({
            "topic": topic,
            "priority_score": round(priority, 2),
            "study_time_minutes": minutes,
            "risk_level": (
                "HIGH" if priority > 0.6 else
                "MEDIUM" if priority > 0.3 else
                "LOW"
            ),
            "mode": (
                "INTENSIVE REVIEW" if topic in weak_set else "STANDARD REVISION"
            )
        })

    # sort most important first
    plan.sort(key=lambda x: x["priority_score"], reverse=True)

    return {
        "student_summary": summary,
        "autopilot_plan": plan
    }


# =====================================================
# 📅 DAILY LEARNING SCHEDULE BUILDER
# =====================================================
def build_daily_schedule(student_id: str, institution_id: str, topics: list):

    study_plan = generate_study_plan(student_id, institution_id, topics)

    schedule = []

    time_slot = 9  # start at 9 AM

    for item in study_plan["autopilot_plan"]:

        schedule.append({
            "time": f"{time_slot}:00",
            "topic": item["topic"],
            "activity": item["mode"],
            "duration_minutes": item["study_time_minutes"]
        })

        time_slot += 1

        if time_slot > 18:
            break

    return {
        "daily_schedule": schedule,
        "total_sessions": len(schedule)
    }


# =====================================================
# 🧠 AUTO EXAM RISK ANALYZER
# =====================================================
def exam_risk_analysis(student_id: str, institution_id: str, topics: list):

    weak_topics = get_weak_topics(student_id, institution_id)
    weak_set = {w["topic"] for w in weak_topics}

    risk_score = 0
    breakdown = []

    for topic in topics:

        results = search_vectors(institution_id, topic, top_k=5)
        avg_score = sum([r.get("score", 0.5) for r in results]) / len(results) if results else 0.5

        if topic in weak_set:
            avg_score -= 0.3

        risk_score += (1 - avg_score)

        breakdown.append({
            "topic": topic,
            "score": round(avg_score * 100, 2)
        })

    final_risk = risk_score / len(topics) if topics else 0

    return {
        "risk_score": round(final_risk, 2),
        "risk_level": (
            "HIGH RISK" if final_risk > 0.6 else
            "MEDIUM RISK" if final_risk > 0.3 else
            "LOW RISK"
        ),
        "breakdown": breakdown
    }