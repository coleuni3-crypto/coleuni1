import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# =====================================================
# 🔐 CONFIG
# =====================================================
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


# =====================================================
# 🚀 CREATE TOKEN
# =====================================================
def create_access_token(data: dict):

    if not SECRET_KEY:
        raise Exception("SECRET_KEY missing")

    payload = data.copy()

    payload.update({
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "type": "access"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# 🔓 VERIFY TOKEN (CORE)
# =====================================================
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if not SECRET_KEY:
        raise Exception("SECRET_KEY not set")

    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =====================================================
# 👤 CURRENT USER
# =====================================================
def get_current_user(user: dict = Depends(verify_token)):
    return user


# =====================================================
# 🔒 ROLE CHECK
# =====================================================
def require_role(role: str):

    def checker(user: dict = Depends(verify_token)):

        if user.get("role") != role:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: requires role {role}"
            )

        return user

    return checker


# =====================================================
# 🏫 INSTITUTION CHECK
# =====================================================
def require_institution(user: dict = Depends(verify_token)):

    institution_id = user.get("institution_id")

    if not institution_id:
        raise HTTPException(
            status_code=403,
            detail="Missing institution context"
        )

    return institution_id