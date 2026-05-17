import re
import bcrypt
from core.supabase_http import select, insert
from auth.auth_utils import create_access_token


# =====================================================
# VALIDATION
# =====================================================
def is_valid_email(email: str):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)


# =====================================================
# SIGNUP
# =====================================================
def signup_user(email: str, password: str, institution_name: str, role="student"):

    email = email.strip().lower()

    if not is_valid_email(email):
        return {"error": "Invalid email"}

    if len(password) < 6:
        return {"error": "Password too short"}

    # check user
    if select("users", "*", {"email": email}, single=True):
        return {"error": "User exists"}

    # institution
    institution = select("institutions", "*", {"name": institution_name}, single=True)

    if institution:
        institution_id = institution["id"]
    else:
        institution_id = insert("institutions", {"name": institution_name})["id"]

    # hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # create user
    user = insert("users", {
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "institution_id": institution_id
    })

    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "institution_id": user["institution_id"]
    })

    return {
        "access_token": token,
        "user": user
    }


# =====================================================
# LOGIN
# =====================================================
def login_user(email: str, password: str):

    email = email.strip().lower()

    user = select("users", "*", {"email": email}, single=True)

    if not user:
        return {"error": "Invalid credentials"}

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "institution_id": user["institution_id"]
    })

    return {
        "access_token": token,
        "user": user
    }