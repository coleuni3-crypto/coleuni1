from core.supabase_http import insert, select
from datetime import datetime
from typing import List, Dict, Any


# =====================================================
# 🔐 INTERNAL SAFETY LAYER
# =====================================================
def _validate(student_id: str, institution_id: str, content: str):

    if not student_id or not institution_id:
        raise ValueError("Missing tenant context")

    if not content or len(content.strip()) < 2:
        return False

    return True


# =====================================================
# 🧠 SAVE MEMORY (STRUCTURED AI CONTEXT STORE)
# =====================================================
def save_memory(student_id: str, institution_id: str, content: str, memory_type: str = "chat"):

    if not _validate(student_id, institution_id, content):
        return None

    return insert("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id,
        "content": content.strip(),
        "memory_type": memory_type,   # chat | lesson | quiz | note
        "importance_score": 1,        # future AI weighting
        "created_at": datetime.utcnow().isoformat()
    })


# =====================================================
# 📥 GET MEMORY (FULL HISTORY - CONTROLLED)
# =====================================================
def get_memory(student_id: str, institution_id: str, limit: int = 50) -> List[Dict[str, Any]]:

    data = select("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    # sort newest first (safe fallback if DB not ordered)
    data = sorted(
        data,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    return data[:limit]


# =====================================================
# 🧠 GET AI MEMORY SUMMARY (CHATBOT CORE CONTEXT)
# =====================================================
def get_memory_summary(student_id: str, institution_id: str):

    data = get_memory(student_id, institution_id)

    if not data:
        return {
            "summary": "No learning history available",
            "recent_interactions": [],
            "memory_strength": 0
        }

    contents = [d.get("content", "") for d in data if d.get("content")]

    memory_strength = min(len(contents) / 50, 1.0)  # normalized score

    return {
        "summary": f"{len(contents)} learning interactions recorded",
        "recent_interactions": contents[:10],
        "memory_strength": round(memory_strength, 2),
        "memory_types": list(set(d.get("memory_type", "unknown") for d in data))
    }


# =====================================================
# 🧠 SMART MEMORY FILTER (AI CONTEXT BUILDER)
# =====================================================
def get_relevant_memory(student_id: str, institution_id: str, keyword: str, limit: int = 10):

    data = get_memory(student_id, institution_id, limit=100)

    keyword = keyword.lower()

    filtered = [
        m for m in data
        if keyword in (m.get("content", "").lower())
    ]

    return filtered[:limit]


# =====================================================
# 📊 MEMORY INSIGHTS ENGINE (LEARNING ANALYTICS)
# =====================================================
def get_memory_insights(student_id: str, institution_id: str):

    data = get_memory(student_id, institution_id)

    if not data:
        return {
            "total_memories": 0,
            "insight": "No data available"
        }

    memory_types = {}

    for d in data:
        t = d.get("memory_type", "unknown")
        memory_types[t] = memory_types.get(t, 0) + 1

    return {
        "total_memories": len(data),
        "memory_distribution": memory_types,
        "insight": (
            "High engagement learner"
            if len(data) > 50 else
            "Moderate engagement"
            if len(data) > 10 else
            "Low engagement"
        )
    }


# =====================================================
# 🧹 MEMORY CLEANUP (ANTI-SPAM / PERFORMANCE SAFE)
# =====================================================
def cleanup_old_memory(student_id: str, institution_id: str, keep: int = 100):

    data = get_memory(student_id, institution_id, limit=1000)

    if len(data) <= keep:
        return {"status": "no_cleanup_needed"}

    # keep newest only
    to_keep = data[:keep]
    to_delete = data[keep:]

    # NOTE: optional delete logic depends on your supabase wrapper
    return {
        "status": "cleanup_ready",
        "kept": len(to_keep),
        "removed_candidates": len(to_delete)
    }