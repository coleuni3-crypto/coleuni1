import re


# =====================================================
# 🧠 PROMPT INJECTION PROTECTION
# =====================================================
def sanitize_query(query: str):

    if not query:
        return ""

    blocked_patterns = [
        "ignore previous instructions",
        "system prompt",
        "reveal prompt",
        "act as system",
        "jailbreak",
        "bypass"
    ]

    q = query.lower()

    for p in blocked_patterns:
        if p in q:
            return "[BLOCKED INPUT DETECTED]"

    return query


# =====================================================
# 🏫 ENSURE TENANT SAFETY
# =====================================================
def enforce_tenant(institution_id: str):

    if not institution_id:
        raise Exception("Missing institution context")

    return institution_id


# =====================================================
# 🧠 LIMIT CONTEXT SIZE (PREVENT OVERLOAD / LEAKS)
# =====================================================
def trim_context(context_list, max_items=5):

    if not context_list:
        return []

    return context_list[:max_items]


# =====================================================
# 🔐 SAFE MEMORY FILTER
# =====================================================
def filter_memory(memory):

    if not memory:
        return {}

    return {
        "summary": memory.get("summary", ""),
        "interactions": memory.get("interactions", [])[-5:]
    }