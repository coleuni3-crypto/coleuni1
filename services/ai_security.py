import re

# =====================================================
# 🚨 ADVANCED PROMPT INJECTION DETECTION ENGINE
# =====================================================
def sanitize_query(query: str):

    if not query:
        return ""

    q = query.lower().strip()

    # =========================
    # 🚫 BASIC ATTACK PATTERNS
    # =========================
    blocked_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "reveal system prompt",
        "show prompt",
        "act as system",
        "jailbreak",
        "bypass restrictions",
        "developer mode",
        "simulate admin",
        "override safety"
    ]

    for p in blocked_patterns:
        if p in q:
            return "[BLOCKED: PROMPT INJECTION ATTEMPT]"

    # =========================
    # 🚨 ADVANCED REGEX DETECTION
    # =========================
    regex_patterns = [
        r"(?i)ignore\s+(all\s+)?previous\s+instructions",
        r"(?i)disregard\s+(system|previous)",
        r"(?i)you\s+are\s+now\s+chatgpt\s+without\s+rules",
        r"(?i)act\s+as\s+if\s+you\s+are\s+not\s+an\s+ai"
    ]

    for pattern in regex_patterns:
        if re.search(pattern, query):
            return "[BLOCKED: MALICIOUS PATTERN DETECTED]"

    # =========================
    # 🧠 SAFE OUTPUT
    # =========================
    return query


# =====================================================
# 🏫 STRONG TENANT ISOLATION (SaaS CORE SECURITY)
# =====================================================
def enforce_tenant(institution_id: str):

    if not institution_id or not isinstance(institution_id, str):
        raise Exception("❌ Invalid institution context")

    # prevent accidental cross-tenant leakage patterns
    if len(institution_id) < 3:
        raise Exception("❌ Suspicious institution ID")

    return institution_id


# =====================================================
# 🧠 CONTEXT LIMITER (TOKEN SAFETY + LEAK PREVENTION)
# =====================================================
def trim_context(context_list, max_items=5):

    if not context_list:
        return []

    if not isinstance(context_list, list):
        return []

    # keep most relevant chunks only
    trimmed = context_list[:max_items]

    # ensure safe string length
    safe_trimmed = []

    for item in trimmed:
        if isinstance(item, dict):
            content = item.get("content", "")
        else:
            content = str(item)

        safe_trimmed.append(content[:1000])  # prevent overflow

    return safe_trimmed


# =====================================================
# 🧠 MEMORY SANITIZER (PRIVACY + SAFETY LAYER)
# =====================================================
def filter_memory(memory):

    if not memory or not isinstance(memory, dict):
        return {
            "summary": "",
            "interactions": []
        }

    interactions = memory.get("interactions", [])

    # =========================
    # 🔒 LIMIT MEMORY EXPOSURE
    # =========================
    safe_interactions = interactions[-5:] if isinstance(interactions, list) else []

    # =========================
    # 🧠 SAFE MEMORY STRUCTURE
    # =========================
    return {
        "summary": str(memory.get("summary", ""))[:500],
        "interactions": safe_interactions
    }


# =====================================================
# 🚨 GLOBAL SECURITY PIPELINE (READY FOR FUTURE AI FIREWALL)
# =====================================================
def security_pipeline(query: str, institution_id: str, memory=None, context=None):

    return {
        "query": sanitize_query(query),
        "institution_id": enforce_tenant(institution_id),
        "memory": filter_memory(memory),
        "context": trim_context(context)
    }