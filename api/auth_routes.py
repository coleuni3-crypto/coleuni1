from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from services.auth_service import signup_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# 📦 REQUEST MODELS (STRICT + CLEAN)
# =====================================================
class LoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class SignupModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    institution_name: str = Field(min_length=2)
    role: str = Field(default="student")


# =====================================================
# 🟢 SIGNUP (UPGRADED FLOW)
# =====================================================
@router.post("/signup")
def signup(data: SignupModel):

    try:
        result = signup_user(
            email=data.email.strip().lower(),
            password=data.password,
            institution_name=data.institution_name.strip(),
            role=data.role.strip().lower()
        )

        # -----------------------------
        # ❌ SERVICE FAILURE HANDLING
        # -----------------------------
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed"
            )

        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # -----------------------------
        # ✅ SUCCESS RESPONSE (STANDARDIZED)
        # -----------------------------
        return {
            "success": True,
            "message": "Account created successfully",
            "data": {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "user": result["user"]
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[AUTH SIGNUP ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup service error"
        )


# =====================================================
# 🔵 LOGIN (UPGRADED FLOW)
# =====================================================
@router.post("/login")
def login(data: LoginModel):

    try:
        result = login_user(
            email=data.email.strip().lower(),
            password=data.password
        )

        # -----------------------------
        # ❌ AUTH FAILURE HANDLING
        # -----------------------------
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"]
            )

        # -----------------------------
        # ✅ SUCCESS RESPONSE (STANDARDIZED)
        # -----------------------------
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "user": result["user"]
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[AUTH LOGIN ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login service error"
        )


# =====================================================
# ❤️ AUTH HEALTH CHECK (ENHANCED)
# =====================================================
@router.get("/health")
def auth_health():

    return {
        "success": True,
        "service": "auth",
        "status": "healthy",
        "version": "coleuni-v4"
    }