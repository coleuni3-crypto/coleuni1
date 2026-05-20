from core.supabase_http import select
from services.student_service import get_student_summary, get_learning_insight
from services.admin_analytics import get_system_analytics


# =====================================================
# 🧱 SAFE CONTEXT EXTRACTOR (REUSABLE CORE)
# =====================================================
def get_context(request):
    user = getattr(request.state, "user", None)

    if not user:
        raise Exception("Unauthorized request")

    return {
        "user_id": user.get("user_id"),
        "institution_id": user.get("institution_id"),
        "role": user.get("role", "student")
    }


# =====================================================
# 🔐 SAFE DB FETCH WRAPPER
# =====================================================
def safe_select(table: str, filters: dict):
    try:
        return select(table, filters) or []
    except Exception:
        return []


# =====================================================
# 👨‍🎓 STUDENT DASHBOARD (UPGRADED)
# =====================================================
def student_dashboard(request):

    ctx = get_context(request)

    student_id = ctx["user_id"]
    institution_id = ctx["institution_id"]

    summary = get_student_summary(student_id, institution_id)
    insights = get_learning_insight(student_id, institution_id)

    return {
        "status": "success",
        "role": "student",
        "student_id": student_id,
        "summary": summary or {},
        "insights": insights or {},
        "recommendation": insights.get("next_step") if isinstance(insights, dict) else None
    }


# =====================================================
# 👨‍🏫 TEACHER DASHBOARD (OPTIMIZED)
# =====================================================
def teacher_dashboard(request):

    ctx = get_context(request)
    institution_id = ctx["institution_id"]

    students = safe_select("users", {
        "institution_id": institution_id,
        "role": "student"
    })

    analytics = get_system_analytics(institution_id)

    return {
        "status": "success",
        "role": "teacher",
        "total_students": len(students),
        "students_sample": students[:30],
        "analytics": analytics,
        "performance_summary": analytics.get("average_score", 0)
    }


# =====================================================
# 🏫 ADMIN DASHBOARD (HARDENED + SCALABLE)
# =====================================================
def admin_dashboard(request):

    ctx = get_context(request)
    institution_id = ctx["institution_id"]

    users = safe_select("users", {
        "institution_id": institution_id
    })

    performance_data = safe_select("student_performance", {
        "institution_id": institution_id
    })

    analytics = get_system_analytics(institution_id)

    role_map = {}
    for u in users:
        role = u.get("role", "unknown")
        role_map[role] = role_map.get(role, 0) + 1

    return {
        "status": "success",
        "role": "admin",
        "total_users": len(users),
        "role_breakdown": role_map,
        "total_students": role_map.get("student", 0),
        "total_teachers": role_map.get("teacher", 0),
        "analytics": analytics,
        "system_load": len(performance_data),
        "health_status": "stable" if len(performance_data) < 10000 else "heavy_load"
    }


# =====================================================
# 🏢 INSTITUTION DASHBOARD (CLEANED)
# =====================================================
def institution_dashboard(request):

    ctx = get_context(request)
    institution_id = ctx["institution_id"]

    analytics = get_system_analytics(institution_id)

    interactions = safe_select("student_memory", {
        "institution_id": institution_id
    })

    return {
        "status": "success",
        "institution_id": institution_id,
        "analytics": analytics,
        "total_interactions": len(interactions),
        "engagement_level": "high" if len(interactions) > 100 else "normal"
    }


# =====================================================
# 🧠 AI INSIGHTS DASHBOARD (UPGRADED INTELLIGENCE)
# =====================================================
def ai_insights_dashboard(request):

    ctx = get_context(request)
    institution_id = ctx["institution_id"]

    analytics = get_system_analytics(institution_id)

    weak = analytics.get("weak_topics", [])
    strong = analytics.get("strong_topics", [])

    # AI recommendation engine (simple logic layer)
    recommendation = "Focus on weak topics to improve performance"

    if weak and len(weak) > 3:
        recommendation = "Critical: multiple weak areas detected"

    if strong and len(strong) > len(weak):
        recommendation = "Strong performance trend detected"

    return {
        "status": "success",
        "weak_topics": weak,
        "strong_topics": strong,
        "recommendation": recommendation,
        "insight_level": "ai-assisted"
    }