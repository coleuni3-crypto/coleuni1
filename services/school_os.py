from core.supabase_http import insert, select
from collections import defaultdict
from datetime import datetime


# =====================================================
# 🔐 INTERNAL SAFE FILTER LAYER (V4 CORE)
# =====================================================
def _build_filter(institution_id: str, location: str = None, extra: dict = None):

    if not institution_id:
        raise ValueError("Missing institution_id (tenant violation)")

    filters = extra or {}
    filters["institution_id"] = institution_id

    if location:
        filters["location"] = location

    return filters


# =====================================================
# 🏫 CREATE CLASS (CAMPUS-AWARE)
# =====================================================
def create_class(institution_id: str, name: str, grade: str, location: str = None):

    if not name or not grade:
        return {"success": False, "error": "Invalid class data"}

    result = insert("classes", {
        "institution_id": institution_id,
        "name": name.strip(),
        "grade": grade.strip(),
        "location": location or "default",
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    })

    return {
        "success": True,
        "class": result
    }


# =====================================================
# 👨‍🏫 ENROLL STUDENT (SAFE + IDEMPOTENT)
# =====================================================
def enroll_student(class_id: int, student_id: str, institution_id: str, location: str = None):

    if not class_id or not student_id:
        return {"success": False, "error": "Missing required fields"}

    filters = _build_filter(
        institution_id,
        location,
        {"class_id": class_id, "student_id": student_id}
    )

    existing = select("enrollments", filters) or []

    if existing:
        return {
            "success": True,
            "status": "already_enrolled"
        }

    result = insert("enrollments", {
        "class_id": class_id,
        "student_id": student_id,
        "institution_id": institution_id,
        "location": location or "default",
        "enrolled_at": datetime.utcnow().isoformat()
    })

    return {
        "success": True,
        "enrollment": result
    }


# =====================================================
# 📊 CLASS PERFORMANCE ANALYTICS (V4 INTELLIGENT)
# =====================================================
def get_class_performance(class_id: int, institution_id: str, location: str = None):

    filters = _build_filter(
        institution_id,
        location,
        {"class_id": class_id}
    )

    results = select("exam_results", filters) or []

    if not results:
        return {
            "class_id": class_id,
            "location": location or "default",
            "average_score": 0,
            "students": 0,
            "performance_level": "no_data",
            "total_exams": 0
        }

    scores = [r.get("score", 0) for r in results if r.get("score") is not None]

    avg = sum(scores) / len(scores) if scores else 0

    return {
        "class_id": class_id,
        "location": location or "default",
        "average_score": round(avg, 2),
        "students": len(set(r.get("student_id") for r in results if r.get("student_id"))),
        "total_exams": len(results),
        "performance_level": (
            "excellent" if avg >= 75 else
            "average" if avg >= 50 else
            "at-risk"
        )
    }


# =====================================================
# 🧠 CLASS RANKINGS (AI-READY STRUCTURE)
# =====================================================
def get_class_rankings(class_id: int, institution_id: str, location: str = None):

    filters = _build_filter(
        institution_id,
        location,
        {"class_id": class_id}
    )

    results = select("exam_results", filters) or []

    student_scores = defaultdict(list)

    for r in results:
        sid = r.get("student_id")
        score = r.get("score", 0)

        if sid:
            student_scores[sid].append(score)

    rankings = []

    for sid, scores in student_scores.items():

        avg = sum(scores) / len(scores) if scores else 0

        rankings.append({
            "student_id": sid,
            "average_score": round(avg, 2),
            "performance_band": (
                "excellent" if avg >= 75 else
                "average" if avg >= 50 else
                "at-risk"
            )
        })

    rankings.sort(key=lambda x: x["average_score"], reverse=True)

    return {
        "class_id": class_id,
        "location": location or "default",
        "total_students": len(rankings),
        "rankings": rankings
    }


# =====================================================
# ⚠️ AT-RISK STUDENTS (EARLY WARNING SYSTEM)
# =====================================================
def get_at_risk_students(class_id: int, institution_id: str, location: str = None):

    filters = _build_filter(
        institution_id,
        location,
        {"class_id": class_id}
    )

    results = select("exam_results", filters) or []

    student_map = defaultdict(list)

    for r in results:
        sid = r.get("student_id")
        score = r.get("score", 0)

        if sid:
            student_map[sid].append(score)

    at_risk = []

    for sid, scores in student_map.items():

        avg = sum(scores) / len(scores)

        if avg < 50:
            at_risk.append({
                "student_id": sid,
                "average_score": round(avg, 2),
                "risk_level": "high" if avg < 40 else "medium"
            })

    return {
        "class_id": class_id,
        "location": location or "default",
        "at_risk_students": at_risk,
        "total_at_risk": len(at_risk)
    }