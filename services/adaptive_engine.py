from datetime import datetime
from core.supabase_http import insert, select, update


# =====================================================
# 🧠 LEARNING EVENT PROCESSOR (ADAPTIVE CORE BRAIN)
# =====================================================
def process_learning_event(student_id: str, institution_id: str, query: str, ai_response):

    try:
        # =========================
        # 📊 SAFE RESPONSE PARSING
        # =========================
        if isinstance(ai_response, dict):
            response_text = (
                ai_response.get("data", {}).get("answer")
                or ai_response.get("answer")
                or str(ai_response)
            )
        else:
            response_text = str(ai_response)

        # =========================
        # 💾 LOG INTERACTION
        # =========================
        insert("ai_interactions", {
            "student_id": student_id,
            "institution_id": institution_id,
            "query": query,
            "response": response_text,
            "created_at": datetime.utcnow().isoformat()
        })

        # =========================
        # 📉 SMART WEAKNESS DETECTION (IMPROVED)
        # =========================
        weak_keywords = [
            "confused",
            "don't understand",
            "hard",
            "difficult",
            "stuck",
            "error",
            "help",
            "explain"
        ]

        query_lower = query.lower()
        is_struggling = any(word in query_lower for word in weak_keywords)

        # =========================
        # 📚 STORE WEAK TOPICS
        # =========================
        if is_struggling:
            insert("weak_topics", {
                "student_id": student_id,
                "institution_id": institution_id,
                "topic": query,
                "strength": "weak",
                "created_at": datetime.utcnow().isoformat()
            })

        # =========================
        # 🧠 STUDENT MEMORY SYSTEM
        # =========================
        memory = select(
            "student_memory",
            {"student_id": student_id},
            single=True
        )

        if memory:
            update(
                "student_memory",
                {"student_id": student_id},
                {
                    "last_activity": datetime.utcnow().isoformat(),
                    "last_query": query
                }
            )
        else:
            insert("student_memory", {
                "student_id": student_id,
                "institution_id": institution_id,
                "last_query": query,
                "last_activity": datetime.utcnow().isoformat(),
                "learning_score": 0
            })

        # =========================
        # 📊 RETURN ENGINE STATUS
        # =========================
        return {
            "tracked": True,
            "is_struggling": is_struggling,
            "engine": "adaptive-v4-core"
        }

    except Exception as e:
        return {
            "tracked": False,
            "error": str(e),
            "engine": "adaptive-v4-core"
        }


# =====================================================
# 🧠 GET STUDENT MEMORY (PERSONALIZATION CORE)
# =====================================================
def get_student_memory(student_id: str, institution_id: str):

    try:
        memory = select(
            "student_memory",
            {"student_id": student_id},
            single=True
        )

        return memory or {
            "student_id": student_id,
            "learning_score": 0,
            "last_activity": None,
            "last_query": None
        }

    except Exception:
        return {
            "student_id": student_id,
            "learning_score": 0
        }


# =====================================================
# ⚠️ WEAK TOPICS ANALYSIS ENGINE
# =====================================================
def get_weak_topics(student_id: str, institution_id: str):

    try:
        topics = select(
            "weak_topics",
            {"student_id": student_id},
            single=False
        )

        if not topics:
            return []

        return [
            t.get("topic")
            for t in topics[-10:]
            if t.get("topic")
        ]

    except Exception:
        return []


# =====================================================
# 📈 LEARNING SCORE CALCULATOR (SAFE + STABLE)
# =====================================================
def update_learning_score(student_id: str, delta: int):

    try:
        memory = select(
            "student_memory",
            {"student_id": student_id},
            single=True
        )

        if not memory:
            return False

        current_score = memory.get("learning_score", 0)
        new_score = max(0, current_score + delta)

        update(
            "student_memory",
            {"student_id": student_id},
            {"learning_score": new_score}
        )

        return new_score

    except Exception:
        return False