from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from core.security import verify_token, require_role, require_institution
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin V5"])


# =====================================================
# 🧠 SAFE ADMIN SERVICE WRAPPER
# =====================================================
def safe_admin_call(func, service: AdminService) -> Dict[str, Any]:

    try:
        result = func()

        return {
            "success": True,
            "engine": "admin-v5-core",
            "data": result,
            "institution_id": service.institution_id,
            "admin_id": service.user.get("user_id")
        }

    except Exception as e:
        print(f"[ADMIN ERROR] {func.__name__}: {str(e)}")

        return {
            "success": False,
            "engine": "admin-v5-core",
            "error": f"{func.__name__} failed",
            "data": {}
        }


# =====================================================
# 🏫 ADMIN OVERVIEW (CORE METRICS DASHBOARD)
# =====================================================
@router.get("/overview")
def overview(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)
    service.institution_id = institution_id

    return safe_admin_call(service.get_overview, service)


# =====================================================
# 🧠 TOP STUDENTS ENGINE (PERFORMANCE ANALYTICS)
# =====================================================
@router.get("/top-students")
def top_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)
    service.institution_id = institution_id

    return safe_admin_call(service.get_top_students, service)


# =====================================================
# ⚠️ AT-RISK STUDENTS ENGINE (AI ALERT SYSTEM)
# =====================================================
@router.get("/at-risk")
def at_risk_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)
    service.institution_id = institution_id

    return safe_admin_call(service.get_at_risk_students, service)


# =====================================================
# 👤 ADMIN PROFILE (SAFE IDENTITY LAYER)
# =====================================================
@router.get("/me")
def current_admin(user=Depends(verify_token)):

    try:
        return {
            "success": True,
            "engine": "admin-profile-v5",
            "data": {
                "id": user.get("user_id"),
                "email": user.get("email"),
                "role": user.get("role"),
                "institution_id": user.get("institution_id")
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# ❤️ HEALTH CHECK (SYSTEM MONITORING)
# =====================================================
@router.get("/health")
def admin_health():

    return {
        "success": True,
        "engine": "admin-v5-core",
        "status": "healthy",
        "features": {
            "multi_tenant": True,
            "rbac": True,
            "analytics": True,
            "ai_monitoring": True
        }
    }