from core.supabase_http import select
from auth.auth_core import create_access_token, verify_password


# =====================================================
# 🔐 LOGIN SERVICE (SUPABASE VERSION)
# =====================================================
def login_user(email: str, password: str):

    # =========================
    # FETCH USER FROM SUPABASE
    # =========================
    user_data = select("users", {"email": email})

    if not user_data:
        return {"error": "Invalid credentials"}

    user = user_data[0]

    # =========================
    # VERIFY PASSWORD (HASHED)
    # =========================
    stored_password = user.get("password")

    if not verify_password(password, stored_password):
        return {"error": "Invalid credentials"}

    # =========================
    # CREATE JWT TOKEN
    # =========================
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "institution_id": user["institution_id"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "institution_id": user["institution_id"]
        }
    }