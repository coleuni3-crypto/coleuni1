from fastapi import Request, HTTPException
from functools import wraps


# =====================================================
# 🧠 GET CURRENT USER (SAFE ACCESS)
# =====================================================
def get_current_user(request: Request):
    """
    Returns authenticated user from request.state
    (set by auth middleware)
    """

    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


# =====================================================
# 🏫 GET INSTITUTION (MULTI-TENANT SAFETY LAYER)
# =====================================================
def get_institution(request: Request):
    """
    Forces SaaS isolation at every request level
    """

    user = get_current_user(request)

    institution_id = user.get("institution_id")

    if not institution_id:
        raise HTTPException(
            status_code=403,
            detail="Institution context missing"
        )

    return institution_id


# =====================================================
# 🔐 ROLE CHECK (SINGLE ROLE)
# =====================================================
def require_role(role: str):
    """
    Protect endpoint with a single role
    """

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            request: Request = kwargs.get("request")

            user = get_current_user(request)

            if user.get("role") != role:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires role: {role}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# =====================================================
# 🔓 MULTI ROLE ACCESS
# =====================================================
def require_any_role(roles: list):
    """
    Allow multiple roles (admin, lecturer, etc.)
    """

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            request: Request = kwargs.get("request")

            user = get_current_user(request)

            if user.get("role") not in roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Allowed roles: {roles}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# =====================================================
# 🏫 SAAS GUARANTEE DECORATOR (INSTITUTION LOCK)
# =====================================================
def require_institution_context(func):
    """
    Ensures every request is scoped to an institution
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):

        request: Request = kwargs.get("request")

        institution_id = get_institution(request)

        # attach for downstream usage
        request.state.institution_id = institution_id

        return await func(*args, **kwargs)

    return wrapper


# =====================================================
# 🔐 COMBINED GUARD (ROLE + INSTITUTION)
# =====================================================
def require_role_and_institution(role: str):
    """
    Production-grade guard for SaaS endpoints
    """

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            request: Request = kwargs.get("request")

            user = get_current_user(request)

            if user.get("role") != role:
                raise HTTPException(
                    status_code=403,
                    detail="Forbidden role"
                )

            institution_id = user.get("institution_id")

            if not institution_id:
                raise HTTPException(
                    status_code=403,
                    detail="Missing institution"
                )

            request.state.institution_id = institution_id

            return await func(*args, **kwargs)

        return wrapper

    return decorator