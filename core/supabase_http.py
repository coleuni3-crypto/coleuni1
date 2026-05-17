import os
from dotenv import load_dotenv
from supabase import create_client, Client

# =====================================================
# 🌍 LOAD ENV
# =====================================================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # IMPORTANT FIX

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =====================================================
# 📥 SELECT
# =====================================================
def select(table: str, columns="*", filters: dict = None, single: bool = False):
    query = supabase.table(table).select(columns)

    if filters:
        for k, v in filters.items():
            query = query.eq(k, v)

    res = query.execute().data

    if single:
        return res[0] if res else None
    return res


# =====================================================
# ➕ INSERT
# =====================================================
def insert(table: str, payload: dict):
    res = supabase.table(table).insert(payload).execute().data
    return res[0] if res else None


# =====================================================
# ✏️ UPDATE
# =====================================================
def update(table: str, payload: dict, filters: dict):
    query = supabase.table(table).update(payload)

    for k, v in filters.items():
        query = query.eq(k, v)

    return query.execute().data


# =====================================================
# ❌ DELETE
# =====================================================
def delete(table: str, filters: dict):
    query = supabase.table(table).delete()

    for k, v in filters.items():
        query = query.eq(k, v)

    return query.execute().data