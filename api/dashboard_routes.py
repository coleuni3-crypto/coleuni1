from fastapi import APIRouter, Request, Depends
from auth.dependencies import get_current_user   # ✅ FIXED IMPORT

from services.dashboard_service import (
    student_dashboard,
    teacher_dashboard,
    admin_dashboard,
    institution_dashboard,
    ai_insights_dashboard
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# =====================================================
# 👨‍🎓 STUDENT
# =====================================================
@router.get("/student")
def student(request: Request, user=Depends(get_current_user)):
    request.state.user = user
    return student_dashboard(request)


# =====================================================
# 👨‍🏫 TEACHER
# =====================================================
@router.get("/teacher")
def teacher(request: Request, user=Depends(get_current_user)):
    request.state.user = user
    return teacher_dashboard(request)


# =====================================================
# 🏫 ADMIN
# =====================================================
@router.get("/admin")
def admin(request: Request, user=Depends(get_current_user)):
    request.state.user = user
    return admin_dashboard(request)


# =====================================================
# 📊 INSTITUTION
# =====================================================
@router.get("/institution")
def institution(request: Request, user=Depends(get_current_user)):
    request.state.user = user
    return institution_dashboard(request)


# =====================================================
# 🧠 AI INSIGHTS
# =====================================================
@router.get("/insights")
def insights(request: Request, user=Depends(get_current_user)):
    request.state.user = user
    return ai_insights_dashboard(request)