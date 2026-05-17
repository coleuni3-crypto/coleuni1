from fastapi import Request
from auth.permissions import get_institution


class BaseService:
    """
    🧠 SaaS CORE LAYER

    Every service inherits:
    - institution isolation
    - request context
    - safe multi-tenant enforcement
    """

    def __init__(self, request: Request):
        self.request = request
        self.user = getattr(request.state, "user", None)

        if not self.user:
            self.institution_id = None
        else:
            self.institution_id = get_institution(request)

        # extra safety
        if not self.institution_id:
            raise Exception("❌ Institution context missing (multi-tenant violation risk)")

    # =====================================================
    # 🏢 STRICT TENANT SCOPE HELPER
    # =====================================================
    def scope_filter(self, base_filter: dict = None):

        """
        Forces every query to ALWAYS include institution_id
        """

        base_filter = base_filter or {}

        base_filter["institution_id"] = self.institution_id

        return base_filter

    # =====================================================
    # 🔒 SAFE ACCESS CHECK
    # =====================================================
    def require_auth(self):

        if not self.user:
            raise Exception("Unauthorized access")

        return self.user

    # =====================================================
    # 🧠 DEBUG CONTEXT (USEFUL DURING DEVELOPMENT)
    # =====================================================
    def debug_context(self):

        return {
            "user": self.user,
            "institution_id": self.institution_id
        }