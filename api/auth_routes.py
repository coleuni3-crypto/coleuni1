from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from services.auth_service import signup_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# =====================================================
# 📦 REQUEST MODELS
# =====================================================

class LoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class SignupModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    institution_name: str = Field(min_length=2)
    role: str = "student"


# =====================================================
# 🟢 SIGNUP
# =====================================================

@router.post("/signup")
def signup(data: SignupModel):

    try:

        result = signup_user(
            email=data.email.lower().strip(),
            password=data.password,
            institution_name=data.institution_name.strip(),
            role=data.role.lower()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed"
            )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return {
            "success": True,
            "message": "Account created successfully",
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": result["user"]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[AUTH SIGNUP ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signup"
        )


# =====================================================
# 🔵 LOGIN
# =====================================================

@router.post("/login")
def login(data: LoginModel):

    try:

        result = login_user(
            email=data.email.lower().strip(),
            password=data.password
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed"
            )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"]
            )

        return {
            "success": True,
            "message": "Login successful",
            "access_token": result["access_token"],
            "token_type": "bearer",
            "user": result["user"]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[AUTH LOGIN ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


# =====================================================
# ❤️ AUTH HEALTH CHECK
# =====================================================

@router.get("/health")
def auth_health():

    return {
        "success": True,
        "service": "auth",
        "status": "healthy"
    }