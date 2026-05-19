from core.supabase_http import insert, select

# =====================================================
# 🧠 SAVE STUDENT PERFORMANCE
# =====================================================
def save_student_performance(user_id, material_id, score, weak_topics=[]):

    return insert("student_progress", {
        "user_id": user_id,
        "material_id": material_id,
        "score": score,
        "weak_topics": weak_topics,
        "attempts": 1
    })


# =====================================================
# 🧠 GET ADAPTIVE LEARNING PATH
# =====================================================
def get_adaptive_content(user_id, material_id):

    progress = select(
        "student_progress",
        {"user_id": user_id, "material_id": material_id},
        single=True
    )

    if not progress:
        return {
            "level": "beginner",
            "focus": "full content"
        }

    score = progress.get("score", 0)

    if score < 50:
        return {
            "level": "weak",
            "focus": "simplified explanations + basics revision"
        }

    elif score < 75:
        return {
            "level": "medium",
            "focus": "mixed revision + practice questions"
        }

    else:
        return {
            "level": "advanced",
            "focus": "exam questions + application problems"
        }