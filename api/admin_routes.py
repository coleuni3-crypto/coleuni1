from fastapi import APIRouter, Depends
from core.security import verify_token, require_role, require_institution
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


# =====================================================
# 🏫 ADMIN OVERVIEW
# =====================================================
@router.get("/overview")
def overview(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)

    return {
        "success": True,
        "institution_id": institution_id,
        "data": service.get_overview()
    }


# =====================================================
# 🧠 TOP STUDENTS
# =====================================================
@router.get("/top-students")
def top_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)

    return {
        "success": True,
        "institution_id": institution_id,
        "data": service.get_top_students()
    }


# =====================================================
# ⚠️ AT RISK STUDENTS
# =====================================================
@router.get("/at-risk")
def at_risk_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    service = AdminService(user)

    return {
        "success": True,
        "institution_id": institution_id,
        "data": service.get_at_risk_students()
    }


# =====================================================
# 👤 CURRENT ADMIN PROFILE
# =====================================================
@router.get("/me")
def current_admin(
    user=Depends(verify_token)
):

    return {
        "success": True,
        "user": {
            "id": user.get("user_id"),
            "email": user.get("email"),
            "role": user.get("role"),
            "institution_id": user.get("institution_id")
        }
    }


# =====================================================
# ❤️ ADMIN HEALTH CHECK
# =====================================================
@router.get("/health")
def admin_health():
    return {
        "success": True,
        "service": "admin_routes",
        "status": "healthy",
        "auth": "active",
        "multi_tenant": True
    }