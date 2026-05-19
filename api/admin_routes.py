from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_token, require_role, require_institution
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


# =====================================================
# 🏫 ADMIN OVERVIEW (V4 CORE DASHBOARD ENGINE)
# =====================================================
@router.get("/overview")
def overview(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    try:
        service = AdminService(user)

        return {
            "success": True,
            "engine": "admin-overview-v4",
            "institution_id": institution_id,
            "data": service.get_overview()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Admin overview failed: {str(e)}"
        )


# =====================================================
# 🧠 TOP STUDENTS ENGINE
# =====================================================
@router.get("/top-students")
def top_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    try:
        service = AdminService(user)

        return {
            "success": True,
            "engine": "admin-top-students-v4",
            "institution_id": institution_id,
            "data": service.get_top_students()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Top students fetch failed: {str(e)}"
        )


# =====================================================
# ⚠️ AT-RISK STUDENTS ENGINE
# =====================================================
@router.get("/at-risk")
def at_risk_students(
    user=Depends(require_role("admin")),
    institution_id=Depends(require_institution)
):

    try:
        service = AdminService(user)

        return {
            "success": True,
            "engine": "admin-risk-analysis-v4",
            "institution_id": institution_id,
            "data": service.get_at_risk_students()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"At-risk analysis failed: {str(e)}"
        )


# =====================================================
# 👤 ADMIN PROFILE
# =====================================================
@router.get("/me")
def current_admin(user=Depends(verify_token)):

    return {
        "success": True,
        "engine": "admin-profile-v4",
        "user": {
            "id": user.get("user_id"),
            "email": user.get("email"),
            "role": user.get("role"),
            "institution_id": user.get("institution_id")
        }
    }


# =====================================================
# ❤️ HEALTH CHECK (ADMIN MODULE)
# =====================================================
@router.get("/health")
def admin_health():

    return {
        "success": True,
        "engine": "admin-module-v4",
        "status": "healthy",
        "auth": "active",
        "multi_tenant": True
    }