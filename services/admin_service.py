from core.supabase_http import select
from typing import List, Dict, Any


# =====================================================
# 🧠 COLEUNI ADMIN SERVICE (V2 - AI READY SAAS CORE)
# =====================================================
class AdminService:

    def __init__(self, user: dict):
        self.user = user
        self.institution_id = user.get("institution_id")


    # =====================================================
    # 📊 OVERVIEW DASHBOARD (CLEAN + SCALABLE)
    # =====================================================
    def get_overview(self):

        users = self._safe_select("users", {})
        attempts = self._safe_select("attempts", {})

        students = self._filter_role(users, "student")
        teachers = self._filter_role(users, "teacher")

        avg_score = self._calculate_institution_average(students)

        return {
            "total_users": len(users),
            "total_students": len(students),
            "total_teachers": len(teachers),
            "total_attempts": len(attempts),

            "average_score": avg_score,
            "performance_level": self._performance_band(avg_score),

            # 🔥 AI-READY METRICS (future expansion)
            "engagement_index": self._calculate_engagement(users, attempts),
            "risk_index": self._calculate_risk_index(students)
        }


    # =====================================================
    # 🏆 TOP STUDENTS (SMART RANKING ENGINE)
    # =====================================================
    def get_top_students(self, limit: int = 10):

        students = self._safe_select("users", {"role": "student"})

        ranked = sorted(
            students,
            key=lambda s: self._student_score(s),
            reverse=True
        )

        return [
            {
                "student_id": s.get("id"),
                "name": s.get("name"),
                "average_score": self._student_score(s),
                "performance_band": self._performance_band(self._student_score(s))
            }
            for s in ranked[:limit]
        ]


    # =====================================================
    # ⚠️ AT-RISK STUDENTS (MULTI-SIGNAL DETECTION)
    # =====================================================
    def get_at_risk_students(self):

        students = self._safe_select("users", {"role": "student"})

        at_risk = []

        for s in students:

            score = self._student_score(s)
            streak = s.get("streak", 0)
            last_active = s.get("last_login")

            risk_score = 0

            # score risk
            if score < 50:
                risk_score += 50
            elif score < 65:
                risk_score += 25

            # inactivity risk
            if not last_active:
                risk_score += 25

            # streak risk
            if streak == 0:
                risk_score += 25

            if risk_score >= 50:
                at_risk.append({
                    "student_id": s.get("id"),
                    "score": score,
                    "risk_score": risk_score,
                    "risk_level": self._risk_level(risk_score)
                })

        return sorted(at_risk, key=lambda x: x["risk_score"], reverse=True)


    # =====================================================
    # 📊 ENGAGEMENT ENGINE (NEW)
    # =====================================================
    def _calculate_engagement(self, users: list, attempts: list) -> float:

        if not users:
            return 0.0

        active_users = len([u for u in users if u.get("last_login")])

        attempt_score = len(attempts)

        return round((active_users * 0.6 + attempt_score * 0.4) / max(len(users), 1), 2)


    # =====================================================
    # ⚠️ RISK INDEX (GLOBAL INSTITUTION HEALTH)
    # =====================================================
    def _calculate_risk_index(self, students: list) -> float:

        if not students:
            return 0.0

        risk_count = len([
            s for s in students
            if self._student_score(s) < 50
        ])

        return round((risk_count / len(students)) * 100, 2)


    # =====================================================
    # 🧠 SCORE ENGINE (FUTURE AI READY)
    # =====================================================
    def _student_score(self, student: dict) -> float:

        return float(
            student.get("score")
            or student.get("learning_score")
            or student.get("avg_score")
            or 0
        )


    # =====================================================
    # 📊 AVERAGE SCORE (INSTITUTION LEVEL)
    # =====================================================
    def _calculate_institution_average(self, students: list) -> float:

        if not students:
            return 0.0

        scores = [self._student_score(s) for s in students]

        return round(sum(scores) / len(scores), 2)


    # =====================================================
    # 🔐 ROLE FILTER
    # =====================================================
    def _filter_role(self, users: list, role: str) -> list:
        return [u for u in users if u.get("role") == role]


    # =====================================================
    # 📈 PERFORMANCE BANDS
    # =====================================================
    def _performance_band(self, score: float) -> str:

        if score >= 75:
            return "excellent"
        elif score >= 50:
            return "average"
        return "at-risk"


    # =====================================================
    # ⚠️ RISK LABELS
    # =====================================================
    def _risk_level(self, risk_score: float) -> str:

        if risk_score >= 75:
            return "critical"
        elif risk_score >= 50:
            return "high"
        return "medium"


    # =====================================================
    # 🔐 SAFE DATABASE ACCESS LAYER
    # =====================================================
    def _safe_select(self, table: str, filters: dict) -> List[Dict[str, Any]]:

        try:
            filters["institution_id"] = self.institution_id

            data = select(table, "*", filters)

            return data or []

        except Exception:
            return []