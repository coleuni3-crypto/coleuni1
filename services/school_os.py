from core.supabase_http import insert, select


# =====================================================
# 🏫 CREATE CLASS
# =====================================================
def create_class(institution_id: str, name: str, grade: str):

    return insert("classes", {
        "institution_id": institution_id,
        "name": name,
        "grade": grade
    })


# =====================================================
# 👨‍🏫 ENROLL STUDENT
# =====================================================
def enroll_student(class_id: int, student_id: str, institution_id: str):

    return insert("enrollments", {
        "class_id": class_id,
        "student_id": student_id,
        "institution_id": institution_id
    })


# =====================================================
# 📊 CLASS PERFORMANCE ANALYTICS
# =====================================================
def get_class_performance(class_id: int, institution_id: str):

    results = select("exam_results", {
        "class_id": class_id,
        "institution_id": institution_id
    })

    if not results:
        return {
            "class_id": class_id,
            "average_score": 0,
            "students": 0
        }

    scores = [r.get("score", 0) for r in results]

    return {
        "class_id": class_id,
        "average_score": round(sum(scores) / len(scores), 2),
        "students": len(set([r["student_id"] for r in results]))
    }


# =====================================================
# 🧠 STUDENT RANKING (SCHOOL WIDE)
# =====================================================
def get_class_rankings(class_id: int, institution_id: str):

    results = select("exam_results", {
        "class_id": class_id,
        "institution_id": institution_id
    })

    student_map = {}

    for r in results:
        sid = r.get("student_id")
        score = r.get("score", 0)

        if sid not in student_map:
            student_map[sid] = []

        student_map[sid].append(score)

    rankings = [
        {
            "student_id": sid,
            "average_score": round(sum(scores) / len(scores), 2)
        }
        for sid, scores in student_map.items()
    ]

    rankings.sort(key=lambda x: x["average_score"], reverse=True)

    return rankings