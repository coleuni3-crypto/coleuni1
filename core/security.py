import os
import jwt

from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# =====================================================
# 🔐 SECURITY CONFIG (PRODUCTION SAFE)
# =====================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise Exception("❌ SECRET_KEY missing in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


# =====================================================
# 🚀 CREATE ACCESS TOKEN (JWT)
# =====================================================
def create_access_token(data: dict):

    try:
        payload = data.copy()

        payload.update({
            "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "type": "access"
        })

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return token

    except Exception as e:
        print("[TOKEN CREATE ERROR]", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )


# =====================================================
# 🔓 VERIFY TOKEN (CORE AUTH GUARD)
# =====================================================
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # =========================
        # 🧠 TOKEN TYPE VALIDATION
        # =========================
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # =========================
        # 🧠 REQUIRED FIELDS CHECK
        # =========================
        if not payload.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    except Exception as e:
        print("[AUTH ERROR]", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


# =====================================================
# 👤 GET CURRENT USER (CLEAN WRAPPER)
# =====================================================
def get_current_user(
    user: dict = Depends(verify_token)
):
    return user


# =====================================================
# 🔒 REQUIRE ROLE (RBAC SYSTEM)
# =====================================================
def require_role(required_role: str):

    def role_checker(
        user: dict = Depends(verify_token)
    ):

        user_role = user.get("role")

        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires role: {required_role}"
            )

        return user

    return role_checker


# =====================================================
# 🏫 REQUIRE INSTITUTION (MULTI-TENANT SAFETY)
# =====================================================
def require_institution(
    user: dict = Depends(verify_token)
):

    institution_id = user.get("institution_id")

    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution access required"
        )

    return institution_id


# =====================================================
# 🧠 REQUIRE ANY ROLE (FLEXIBLE ACCESS CONTROL)
# =====================================================
def require_any_role(allowed_roles: list):

    def role_checker(
        user: dict = Depends(verify_token)
    ):

        role = user.get("role")

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return role_checker