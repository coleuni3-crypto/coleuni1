from fastapi import Request
from auth.permissions import get_institution
import os


# =====================================================
# 🧠 COLEUNI SAAS CORE KERNEL v2
# =====================================================
class BaseService:
    """
    🧠 SaaS CORE LAYER (MULTI-TENANT SAFE)

    Features:
    - Strict institution isolation
    - Safe request context extraction
    - Role-ready architecture
    - Production-safe debugging
    - Future RBAC expansion ready
    """

    def __init__(self, request: Request):

        self.request = request
        self.user = getattr(request.state, "user", None)

        # =================================================
        # 🏢 INSTITUTION CONTEXT ENFORCEMENT
        # =================================================
        self.institution_id = get_institution(request) if self.user else None

        if not self.institution_id:
            raise Exception("❌ Multi-tenant violation: missing institution context")

        # =================================================
        # 🧠 ROLE (FUTURE RBAC READY)
        # =================================================
        self.role = self.user.get("role") if self.user else None

        # =================================================
        # 🔐 ENV MODE (DEV / PROD SAFETY SWITCH)
        # =================================================
        self.is_dev = os.getenv("ENV", "dev") == "dev"

    # =====================================================
    # 🏢 STRICT TENANT QUERY SCOPING
    # =====================================================
    def scope_filter(self, base_filter: dict = None):

        base_filter = base_filter or {}

        if not isinstance(base_filter, dict):
            raise Exception("Invalid filter type")

        # FORCE TENANT ISOLATION
        base_filter["institution_id"] = self.institution_id

        return base_filter

    # =====================================================
    # 🔐 AUTHENTICATION CHECK
    # =====================================================
    def require_auth(self):

        if not self.user:
            raise Exception("Unauthorized request")

        return self.user

    # =====================================================
    # 🛡 ROLE CHECK SYSTEM (RBAC READY)
    # =====================================================
    def require_role(self, allowed_roles: list):

        if not self.user:
            raise Exception("Unauthorized")

        if self.role not in allowed_roles:
            raise Exception(
                f"Forbidden: requires role in {allowed_roles}"
            )

        return True

    # =====================================================
    # 🧠 SAFE USER CONTEXT BUILDER
    # =====================================================
    def get_context(self):

        return {
            "user_id": self.user.get("user_id"),
            "email": self.user.get("email"),
            "role": self.role,
            "institution_id": self.institution_id
        }

    # =====================================================
    # 🔍 DEBUG CONTEXT (DEV ONLY SAFETY)
    # =====================================================
    def debug_context(self):

        if not self.is_dev:
            return {
                "error": "Debug disabled in production"
            }

        return {
            "user": self.user,
            "role": self.role,
            "institution_id": self.institution_id,
            "env": "development"
        }

    # =====================================================
    # 🚨 SAFETY WRAPPER (FUTURE AI GUARD HOOK)
    # =====================================================
    def safe_execute(self, func, *args, **kwargs):

        """
        Wrapper for safe service execution
        (future: AI firewall / logging / audit)
        """

        try:
            return func(*args, **kwargs)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service": "base_service_v2"
            }