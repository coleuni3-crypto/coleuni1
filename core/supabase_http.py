import os
from dotenv import load_dotenv
from supabase import create_client, Client

# ==============================
# 🌍 LOAD ENV
# ==============================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==============================
# 🧠 SAFE RESPONSE WRAPPER
# ==============================
def safe_data(response):
    try:
        return response.data if hasattr(response, "data") else response
    except Exception:
        return []


# ==============================
# 📥 SELECT (SAFE + FILTERED)
# ==============================
def select(table: str, filters: dict = None, columns="*", single=False):
    try:
        query = supabase.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        res = query.execute()
        data = safe_data(res)

        if single:
            return data[0] if data else None

        return data

    except Exception as e:
        print(f"[SUPABASE SELECT ERROR] {table}: {e}")
        return []


# ==============================
# ➕ INSERT
# ==============================
def insert(table: str, payload: dict):
    try:
        res = supabase.table(table).insert(payload).execute()
        data = safe_data(res)
        return data[0] if data else None

    except Exception as e:
        print(f"[SUPABASE INSERT ERROR] {table}: {e}")
        return None


# ==============================
# ✏️ UPDATE
# ==============================
def update(table: str, payload: dict, filters: dict):
    try:
        query = supabase.table(table).update(payload)

        for key, value in filters.items():
            query = query.eq(key, value)

        res = query.execute()
        return safe_data(res)

    except Exception as e:
        print(f"[SUPABASE UPDATE ERROR] {table}: {e}")
        return []


# ==============================
# ❌ DELETE
# ==============================
def delete(table: str, filters: dict):
    try:
        query = supabase.table(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        res = query.execute()
        return safe_data(res)

    except Exception as e:
        print(f"[SUPABASE DELETE ERROR] {table}: {e}")
        return []