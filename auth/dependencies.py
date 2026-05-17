from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.core import decode_token

security = HTTPBearer()


# =====================================================
# 🔐 GET CURRENT USER
# =====================================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    return decode_token(token)


# =====================================================
# 🛡 ROLE CHECK
# =====================================================
def require_role(role: str):

    def checker(user: dict = Depends(get_current_user)):

        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")

        return user

    return checker


# =====================================================
# 🏫 INSTITUTION CHECK
# =====================================================
def require_institution(user: dict = Depends(get_current_user)):

    if not user.get("institution_id"):
        raise HTTPException(status_code=403, detail="Missing institution")

    return user["institution_id"]