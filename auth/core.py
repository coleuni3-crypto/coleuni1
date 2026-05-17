import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 7


# =====================================================
# 🔐 CREATE TOKEN
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
# 🔓 DECODE TOKEN
# =====================================================
def decode_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")