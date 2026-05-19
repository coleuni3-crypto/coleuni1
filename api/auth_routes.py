from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.auth_service import signup_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

# =====================================================
# 📦 REQUEST MODELS
# =====================================================

class LoginModel(BaseModel):
    email: EmailStr
    password: str


class SignupModel(BaseModel):
    email: EmailStr
    password: str
    institution_name: str
    role: str = "student"

# =====================================================
# 🟢 SIGNUP
# =====================================================
@router.post("/signup")
def signup(data: SignupModel):

    try:
        result = signup_user(
            email=data.email.lower(),
            password=data.password,
            institution_name=data.institution_name,
            role=data.role
        )

        # ✅ FRONTEND expects access_token + user
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": result["user"]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[SIGNUP ERROR]", e)
        raise HTTPException(
            status_code=500,
            detail="Signup failed. Try again later."
        )

# =====================================================
# 🔵 LOGIN
# =====================================================
@router.post("/login")
def login(data: LoginModel):

    try:
        result = login_user(
            email=data.email.lower(),
            password=data.password
        )

        # ✅ CRITICAL FIX: match frontend expectations
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": result["user"]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[LOGIN ERROR]", e)
        raise HTTPException(
            status_code=500,
            detail="Login failed. Try again later."
        )