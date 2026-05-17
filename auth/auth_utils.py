import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import load_dotenv

# =====================================================
# 🌍 LOAD ENV SAFELY
# =====================================================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 7


if not SECRET_KEY:
    raise Exception("❌ SECRET_KEY missing in environment variables")


# =====================================================
# 🔐 CREATE ACCESS TOKEN (SAAS-READY)
# =====================================================
def create_access_token(data: dict):
    """
    Creates a signed JWT token with SaaS claims
    """

    payload = data.copy()

    payload.update({
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "type": "access",

        # 🔥 SAFETY: add token identifier for future logout system
        "token_id": os.urandom(12).hex()
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# 🔓 DECODE + VALIDATE TOKEN
# =====================================================
def decode_token(token: str):
    """
    Validates and decodes JWT token
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # =========================
        # TYPE VALIDATION
        # =========================
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        return payload

    # =========================
    # EXPIRY ERROR
    # =========================
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    # =========================
    # INVALID TOKEN
    # =========================
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # =========================
    # CATCH ALL (SAFETY NET)
    # =========================
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )