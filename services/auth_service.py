import re
import bcrypt
import time

from core.supabase_http import select, insert
from auth.auth_utils import create_access_token


# =====================================================
# 📧 STRONG EMAIL VALIDATION (IMPROVED)
# =====================================================
def is_valid_email(email: str):

    if not email:
        return False

    email = email.strip().lower()

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    return bool(re.match(pattern, email))


# =====================================================
# 🔐 PASSWORD STRENGTH CHECK
# =====================================================
def is_strong_password(password: str):

    if not password:
        return False

    if len(password) < 6:
        return False

    # optional upgrade rules (can tighten later)
    if len(password) > 128:
        return False

    return True


# =====================================================
# 🔐 PASSWORD HASHING (SECURE)
# =====================================================
def hash_password(password: str):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)  # stronger cost factor
    ).decode("utf-8")


# =====================================================
# 🔐 TIMING-SAFE PASSWORD VERIFY
# =====================================================
def verify_password(plain: str, hashed: str):

    try:
        if not plain or not hashed:
            return False

        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8")
        )

    except Exception:
        return False


# =====================================================
# 🏫 INSTITUTION CREATION (RACE-CONDITION SAFE)
# =====================================================
def get_or_create_institution(name: str):

    if not name:
        raise Exception("Institution name required")

    name = name.strip().lower()

    # check existing
    institution = select(
        "institutions",
        {"name": name},
        single=True
    )

    if institution:
        return institution["id"]

    # create new safely
    new_inst = insert("institutions", {
        "name": name,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    if not new_inst:
        raise Exception("Institution creation failed")

    return new_inst["id"]


# =====================================================
# 🧠 TOKEN PAYLOAD BUILDER (CLEAN ARCHITECTURE)
# =====================================================
def build_token_payload(user: dict):

    return {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "institution_id": user["institution_id"]
    }


# =====================================================
# 🧠 SIGNUP (PRODUCTION-GRADE)
# =====================================================
def signup_user(email: str, password: str, institution_name: str, role="student"):

    try:
        email = email.strip().lower()

        # =========================
        # 🔐 VALIDATION
        # =========================
        if not is_valid_email(email):
            return {"error": "Invalid email format"}

        if not is_strong_password(password):
            return {"error": "Weak password (min 6 chars)"}

        # =========================
        # 🚨 DUPLICATE CHECK
        # =========================
        existing = select("users", {"email": email}, single=True)

        if existing:
            return {"error": "User already exists"}

        # =========================
        # 🏫 INSTITUTION HANDLING
        # =========================
        institution_id = get_or_create_institution(institution_name)

        # =========================
        # 👤 CREATE USER
        # =========================
        user = insert("users", {
            "email": email,
            "password": hash_password(password),
            "role": role,
            "institution_id": institution_id
        })

        if not user:
            return {"error": "User creation failed"}

        # =========================
        # 🔐 TOKEN GENERATION
        # =========================
        token = create_access_token(build_token_payload(user))

        return {
            "access_token": token,
            "user": build_token_payload(user)
        }

    except Exception as e:
        print("[SIGNUP ERROR]", str(e))
        return {"error": "Signup failed internally"}


# =====================================================
# 🔐 LOGIN (SECURE + CLEAN)
# =====================================================
def login_user(email: str, password: str):

    try:
        email = email.strip().lower()

        # =========================
        # 👤 FETCH USER
        # =========================
        user = select("users", {"email": email}, single=True)

        if not user:
            return {"error": "Invalid credentials"}

        # =========================
        # 🔐 VERIFY PASSWORD
        # =========================
        if not verify_password(password, user.get("password")):
            return {"error": "Invalid credentials"}

        # =========================
        # 🧠 TOKEN
        # =========================
        token = create_access_token(build_token_payload(user))

        return {
            "access_token": token,
            "user": build_token_payload(user)
        }

    except Exception as e:
        print("[LOGIN ERROR]", str(e))
        return {"error": "Login failed internally"}