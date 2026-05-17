from core.supabase_http import insert, select
from datetime import datetime


# =====================================================
# 🧠 SAVE MEMORY (AI LEARNING CONTEXT)
# =====================================================
def save_memory(student_id: str, institution_id: str, content: str):

    if not content or len(content.strip()) < 2:
        return None

    return insert("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id,
        "content": content.strip(),
        "created_at": datetime.utcnow().isoformat()
    })


# =====================================================
# 📥 GET RAW MEMORY (FULL HISTORY)
# =====================================================
def get_memory(student_id: str, institution_id: str):

    data = select("student_memory", {
        "student_id": student_id,
        "institution_id": institution_id
    }) or []

    return data


# =====================================================
# 🧠 GET AI MEMORY SUMMARY (IMPORTANT FOR CHATBOT)
# =====================================================
def get_memory_summary(student_id: str, institution_id: str):

    data = get_memory(student_id, institution_id)

    if not data:
        return {
            "summary": "No learning history available",
            "recent_interactions": []
        }

    interactions = [
        d.get("content", "")
        for d in data
        if d.get("content")
    ]

    return {
        "summary": f"{len(interactions)} total learning interactions",
        "recent_interactions": interactions[-10:]
    }