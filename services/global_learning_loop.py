from core.supabase_http import supabase
from services.global_ai_engine import calculate_mastery, next_review_date


# =====================================================
# 🔁 UPDATE STUDENT PERFORMANCE
# =====================================================
def update_learning_progress(student_id, institution_id, topic, correct):

    table = supabase.table("student_learning_profile")

    existing = table.select("*") \
        .eq("student_id", student_id) \
        .eq("topic", topic) \
        .execute()

    if existing.data:

        record = existing.data[0]

        attempts = record["attempts"] + 1
        correct_total = record["correct"] + (1 if correct else 0)

        mastery = calculate_mastery(correct_total, attempts)

        table.update({
            "attempts": attempts,
            "correct": correct_total,
            "mastery_level": mastery,
            "next_review": next_review_date(mastery).isoformat(),
            "last_seen": "now()"
        }).eq("id", record["id"]).execute()

    else:

        table.insert({
            "student_id": student_id,
            "institution_id": institution_id,
            "topic": topic,
            "attempts": 1,
            "correct": 1 if correct else 0,
            "mastery_level": 1.0 if correct else 0.0,
            "next_review": next_review_date(0.5).isoformat()
        }).execute()