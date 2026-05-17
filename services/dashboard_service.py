from core.supabase_http import select
from services.student_service import get_student_summary, get_learning_insight
from services.admin_analytics import get_system_analytics


# =====================================================
# 👨‍🎓 STUDENT DASHBOARD
# =====================================================
def student_dashboard(request):

    user = request.state.user

    student_id = user["user_id"]
    institution_id = user["institution_id"]

    summary = get_student_summary(student_id, institution_id)
    insights = get_learning_insight(student_id, institution_id)

    return {
        "student_id": student_id,
        "summary": summary,
        "insights": insights,
        "status": "active"
    }


# =====================================================
# 👨‍🏫 TEACHER DASHBOARD
# =====================================================
def teacher_dashboard(request):

    user = request.state.user
    institution_id = user["institution_id"]

    students = select("users", {
        "institution_id": institution_id,
        "role": "student"
    })

    analytics = get_system_analytics(institution_id)

    return {
        "total_students": len(students),
        "students": students[:50],
        "analytics": analytics,
        "status": "teacher_view"
    }


# =====================================================
# 🏫 ADMIN DASHBOARD
# =====================================================
def admin_dashboard(request):

    user = request.state.user
    institution_id = user["institution_id"]

    users = select("users", {
        "institution_id": institution_id
    })

    analytics = get_system_analytics(institution_id)

    performance_data = select("student_performance", {
        "institution_id": institution_id
    })

    return {
        "total_users": len(users),
        "total_students": len([u for u in users if u["role"] == "student"]),
        "total_admins": len([u for u in users if u["role"] == "admin"]),
        "analytics": analytics,
        "system_load": len(performance_data),
        "status": "admin_control_panel"
    }


# =====================================================
# 📊 INSTITUTION DASHBOARD
# =====================================================
def institution_dashboard(request):

    user = request.state.user
    institution_id = user["institution_id"]

    analytics = get_system_analytics(institution_id)

    interactions = select("student_memory", {
        "institution_id": institution_id
    })

    return {
        "institution_id": institution_id,
        "analytics": analytics,
        "total_interactions": len(interactions),
        "status": "live"
    }


# =====================================================
# 🧠 AI INSIGHTS DASHBOARD
# =====================================================
def ai_insights_dashboard(request):

    user = request.state.user
    institution_id = user["institution_id"]

    analytics = get_system_analytics(institution_id)

    return {
        "weak_topics": analytics.get("weak_topics", []),
        "strong_topics": analytics.get("strong_topics", []),
        "recommendation": "Focus on weak topics to improve performance",
        "status": "ai_insights_ready"
    }