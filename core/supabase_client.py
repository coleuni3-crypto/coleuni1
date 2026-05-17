from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase env variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# GENERIC DB OPERATIONS
# =========================

def insert(table: str, data: dict):
    return supabase.table(table).insert(data).execute()


def select(table: str, filters: dict = None):
    query = supabase.table(table).select("*")

    if filters:
        for k, v in filters.items():
            query = query.eq(k, v)

    return query.execute()


def delete(table: str, filters: dict):
    query = supabase.table(table)

    for k, v in filters.items():
        query = query.eq(k, v)

    return query.delete().execute()