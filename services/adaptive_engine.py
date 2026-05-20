from datetime import datetime
from core.supabase_http import insert, select, update


# =====================================================
# 🧠 SMART STRUGGLE DETECTOR (NEW CORE LOGIC)
# =====================================================
def detect_struggle(query: str, response: str):

    query = (query or "").lower()
    response = (response or "").lower()

    signals = [
        "i don't know",
        "not sure",
        "confused",
        "hard",
        "difficult",
        "stuck",
        "explain again",
        "still don't understand",
        "i don't get it"
    ]

    score = sum(1 for s in signals if s in query or s in response)

    return score >= 2


# =====================================================
# 🧠 LEARNING EVENT PROCESSOR (V5 CORE BRAIN)
# =====================================================
def process_learning_event(student_id: str, institution_id: str, query: str, ai_response):

    try:

        # =========================
        # 📊 RESPONSE NORMALIZATION
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
        # 🧠 STRUGGLE DETECTION (V5)
        # =========================
        is_struggling = detect_struggle(query, response_text)

        # =========================
        # 💾 LOG FULL INTERACTION
        # =========================
        insert("ai_interactions", {
            "student_id": student_id,
            "institution_id": institution_id,
            "query": query,
            "response": response_text,
            "is_struggling": is_struggling,
            "created_at": datetime.utcnow().isoformat()
        })

        # =========================
        # 📉 WEAK TOPIC ENGINE (SMART)
        # =========================
        if is_struggling:
            insert("weak_topics", {
                "student_id": student_id,
                "institution_id": institution_id,
                "topic": query,
                "severity": 2,
                "strength": "weak",
                "created_at": datetime.utcnow().isoformat()
            })

        # =========================
        # 🧠 STUDENT MEMORY ENGINE (V5)
        # =========================
        memory = select(
            "student_memory",
            {"student_id": student_id},
            single=True
        )

        if memory:

            learning_score = memory.get("learning_score", 0)
            streak = memory.get("streak", 0)
            confidence = memory.get("confidence", 50)

            # =========================
            # 📈 INTELLIGENT SCORING MODEL
            # =========================
            if is_struggling:
                delta = -3
                streak = 0
                confidence = max(0, confidence - 5)
            else:
                delta = +2
                streak += 1
                confidence = min(100, confidence + 2)

            new_score = max(0, learning_score + delta)

            update(
                "student_memory",
                {"student_id": student_id},
                {
                    "last_activity": datetime.utcnow().isoformat(),
                    "last_query": query,
                    "learning_score": new_score,
                    "streak": streak,
                    "confidence": confidence,
                    "last_struggle": datetime.utcnow().isoformat() if is_struggling else memory.get("last_struggle"),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

        else:

            insert("student_memory", {
                "student_id": student_id,
                "institution_id": institution_id,
                "last_query": query,
                "last_activity": datetime.utcnow().isoformat(),
                "learning_score": 1,
                "streak": 1,
                "confidence": 50,
                "last_struggle": None,
                "created_at": datetime.utcnow().isoformat()
            })

        return {
            "tracked": True,
            "is_struggling": is_struggling,
            "engine": "adaptive-memory-v5"
        }

    except Exception as e:
        return {
            "tracked": False,
            "error": str(e),
            "engine": "adaptive-memory-v5"
        }


# =====================================================
# 🧠 GET STUDENT MEMORY (RICH PROFILE)
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
            "streak": 0,
            "confidence": 50,
            "last_activity": None,
            "last_query": None,
            "last_struggle": None
        }

    except Exception:
        return {
            "student_id": student_id,
            "learning_score": 0,
            "streak": 0,
            "confidence": 50
        }


# =====================================================
# ⚠️ WEAK TOPIC ENGINE (RANKED)
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

        # sort by severity (MOST IMPORTANT IMPROVEMENT)
        sorted_topics = sorted(
            topics,
            key=lambda x: x.get("severity", 1),
            reverse=True
        )

        return [
            {
                "topic": t.get("topic"),
                "severity": t.get("severity", 1)
            }
            for t in sorted_topics[:10]
        ]

    except Exception:
        return []


# =====================================================
# 📈 LEARNING SCORE SYSTEM (SAFE + CONTROLLED)
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

        # safety clamp (prevents score explosion)
        new_score = max(0, min(1000, current_score + delta))

        update(
            "student_memory",
            {"student_id": student_id},
            {
                "learning_score": new_score,
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        return new_score

    except Exception:
        return False