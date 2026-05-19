from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Callable, Any

from core.security import get_current_user

from services.dashboard_service import (
    student_dashboard,
    teacher_dashboard,
    admin_dashboard,
    institution_dashboard,
    ai_insights_dashboard
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# =====================================================
# 🧠 SAFE DASHBOARD EXECUTOR (CORE WRAPPER)
# =====================================================
def safe_run(func: Callable, request: Request):
    """
    Ensures dashboard never crashes frontend.
    """
    try:
        result = func(request)

        return {
            "success": True,
            "data": result,
            "engine": "dashboard-v4-safe"
        }

    except Exception as e:
        print(f"[DASHBOARD ERROR] {func.__name__}:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"{func.__name__} failed"
        )


# =====================================================
# 👨‍🎓 STUDENT DASHBOARD
# =====================================================
@router.get("/student")
def student(request: Request, user=Depends(get_current_user)):

    request.state.user = user

    return safe_run(student_dashboard, request)


# =====================================================
# 👨‍🏫 TEACHER DASHBOARD
# =====================================================
@router.get("/teacher")
def teacher(request: Request, user=Depends(get_current_user)):

    request.state.user = user

    return safe_run(teacher_dashboard, request)


# =====================================================
# 🏫 ADMIN DASHBOARD
# =====================================================
@router.get("/admin")
def admin(request: Request, user=Depends(get_current_user)):

    request.state.user = user

    return safe_run(admin_dashboard, request)


# =====================================================
# 🏫 INSTITUTION DASHBOARD
# =====================================================
@router.get("/institution")
def institution(request: Request, user=Depends(get_current_user)):

    request.state.user = user

    return safe_run(institution_dashboard, request)


# =====================================================
# 🧠 AI INSIGHTS DASHBOARD
# =====================================================
@router.get("/insights")
def insights(request: Request, user=Depends(get_current_user)):

    request.state.user = user

    return safe_run(ai_insights_dashboard, request)