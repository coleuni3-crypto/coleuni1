import re
import bcrypt

from core.supabase_http import select, insert
from auth.auth_utils import create_access_token

# =====================================================
# 📧 EMAIL VALIDATION
# =====================================================
def is_valid_email(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# =====================================================
# 🔐 HASH PASSWORD
# =====================================================
def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# =====================================================
# 🔐 VERIFY PASSWORD
# =====================================================
def verify_password(plain: str, hashed: str):
    try:
        return bcrypt.checkpw(
            plain.encode(),
            hashed.encode()
        )
    except Exception:
        return False

# =====================================================
# 🏫 GET OR CREATE INSTITUTION
# =====================================================
def get_or_create_institution(name: str):

    institution = select(
        "institutions",
        {"name": name},
        single=True
    )

    if institution:
        return institution["id"]

    new_inst = insert("institutions", {
        "name": name
    })

    if not new_inst:
        raise Exception("Failed to create institution")

    return new_inst["id"]

# =====================================================
# 🧠 SIGNUP USER
# =====================================================
def signup_user(email: str, password: str, institution_name: str, role="student"):

    email = email.strip().lower()

    # validation
    if not is_valid_email(email):
        return {"error": "Invalid email format"}

    if len(password) < 6:
        return {"error": "Password must be at least 6 characters"}

    # check existing user
    existing = select("users", {"email": email}, single=True)

    if existing:
        return {"error": "User already exists"}

    try:
        institution_id = get_or_create_institution(institution_name)

        # create user
        user = insert("users", {
            "email": email,
            "password": hash_password(password),
            "role": role,
            "institution_id": institution_id
        })

        if not user:
            return {"error": "Failed to create user"}

        token = create_access_token({
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "institution_id": user["institution_id"]
        })

        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "institution_id": user["institution_id"]
            }
        }

    except Exception as e:
        print("[SIGNUP ERROR]", e)

        return {
            "error": "Signup failed"
        }

# =====================================================
# 🔐 LOGIN USER
# =====================================================
def login_user(email: str, password: str):

    email = email.strip().lower()

    try:
        user = select("users", {"email": email}, single=True)

        if not user:
            return {"error": "Invalid credentials"}

        stored_password = user.get("password")

        if not stored_password:
            return {"error": "Account misconfigured"}

        if not verify_password(password, stored_password):
            return {"error": "Invalid credentials"}

        token = create_access_token({
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "institution_id": user["institution_id"]
        })

        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "institution_id": user["institution_id"]
            }
        }

    except Exception as e:
        print("[LOGIN ERROR]", e)

        return {
            "error": "Login failed"
        }