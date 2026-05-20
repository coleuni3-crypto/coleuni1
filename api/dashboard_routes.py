from fastapi import APIRouter, Depends, HTTPException, status
from typing import Callable, Dict, Any, Optional

from core.security import get_current_user

from services.dashboard_service import (
    student_dashboard,
    teacher_dashboard,
    admin_dashboard,
    institution_dashboard,
    ai_insights_dashboard
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard V5"])


# =====================================================
# 🧠 ROLE GUARD (SECURITY LAYER)
# =====================================================
def require_role(user: dict, allowed_roles: list[str]):
    role = user.get("role")

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user role"
        )

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this role"
        )


# =====================================================
# 🧠 SAFE DASHBOARD EXECUTOR (V5 CORE WRAPPER)
# =====================================================
def safe_run(func: Callable, user: dict) -> Dict[str, Any]:

    try:
        result = func(user)

        return {
            "success": True,
            "engine": "dashboard-v5-core",
            "data": result,
            "user_role": user.get("role"),
            "user_id": user.get("user_id")
        }

    except Exception as e:
        print(f"[DASHBOARD ERROR] {func.__name__}: {str(e)}")

        return {
            "success": False,
            "engine": "dashboard-v5-core",
            "error": f"{func.__name__} failed",
            "data": {}
        }


# =====================================================
# 👨‍🎓 STUDENT DASHBOARD
# =====================================================
@router.get("/student")
def student(user=Depends(get_current_user)):

    require_role(user, ["student"])

    return safe_run(student_dashboard, user)


# =====================================================
# 👨‍🏫 TEACHER DASHBOARD
# =====================================================
@router.get("/teacher")
def teacher(user=Depends(get_current_user)):

    require_role(user, ["teacher", "admin"])

    return safe_run(teacher_dashboard, user)


# =====================================================
# 🏫 ADMIN DASHBOARD
# =====================================================
@router.get("/admin")
def admin(user=Depends(get_current_user)):

    require_role(user, ["admin"])

    return safe_run(admin_dashboard, user)


# =====================================================
# 🏫 INSTITUTION DASHBOARD
# =====================================================
@router.get("/institution")
def institution(user=Depends(get_current_user)):

    require_role(user, ["admin", "teacher"])

    return safe_run(institution_dashboard, user)


# =====================================================
# 🧠 AI INSIGHTS DASHBOARD (ALL ROLES)
# =====================================================
@router.get("/insights")
def insights(user=Depends(get_current_user)):

    return safe_run(ai_insights_dashboard, user)