from datetime import datetime
from core.supabase_http import supabase
from services.global_ai_engine import calculate_mastery, next_review_date


# =====================================================
# 🔁 UPDATE STUDENT PERFORMANCE (COLEUNI CORE v3)
# =====================================================
def update_learning_progress(student_id, institution_id, topic, correct):

    table = supabase.table("student_learning_profile")

    try:

        # =================================================
        # 📊 FETCH EXISTING RECORD (OPTIMIZED QUERY)
        # =================================================
        response = table.select(
            "id, attempts, correct"
        ).eq(
            "student_id", student_id
        ).eq(
            "institution_id", institution_id
        ).eq(
            "topic", topic
        ).limit(1).execute()

        record = response.data[0] if response.data else None

        now = datetime.utcnow().isoformat()

        # =================================================
        # 🧠 UPDATE PATH (EXISTING RECORD)
        # =================================================
        if record:

            attempts = (record.get("attempts") or 0) + 1
            correct_total = (record.get("correct") or 0) + (1 if correct else 0)

            mastery = calculate_mastery(correct_total, attempts)
            next_review = next_review_date(mastery).isoformat()

            update_payload = {
                "attempts": attempts,
                "correct": correct_total,
                "mastery_level": mastery,
                "next_review": next_review,
                "last_seen": now,
                "updated_at": now
            }

            table.update(update_payload).eq("id", record["id"]).execute()

            return {
                "success": True,
                "status": "updated",
                "engine": "learning-progress-v3",
                "data": {
                    "topic": topic,
                    "mastery": mastery,
                    "attempts": attempts,
                    "correct": correct_total
                }
            }

        # =================================================
        # 🆕 CREATE PATH (NEW RECORD)
        # =================================================
        attempts = 1
        correct_total = 1 if correct else 0

        mastery = calculate_mastery(correct_total, attempts)
        next_review = next_review_date(mastery).isoformat()

        insert_payload = {
            "student_id": student_id,
            "institution_id": institution_id,
            "topic": topic,
            "attempts": attempts,
            "correct": correct_total,
            "mastery_level": mastery,
            "next_review": next_review,
            "last_seen": now,
            "created_at": now,
            "updated_at": now
        }

        table.insert(insert_payload).execute()

        return {
            "success": True,
            "status": "created",
            "engine": "learning-progress-v3",
            "data": {
                "topic": topic,
                "mastery": mastery,
                "attempts": attempts,
                "correct": correct_total
            }
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "engine": "learning-progress-v3",
            "message": str(e)
        }