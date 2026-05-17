from fastapi import APIRouter
from pydantic import BaseModel
from services.auth_service import signup_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginModel(BaseModel):
    email: str
    password: str


class SignupModel(BaseModel):
    email: str
    password: str
    institution_name: str
    role: str = "student"


@router.post("/signup")
def signup(data: SignupModel):
    return signup_user(
        data.email,
        data.password,
        data.institution_name,
        data.role
    )


@router.post("/login")
def login(data: LoginModel):
    return login_user(data.email, data.password)