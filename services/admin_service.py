from core.supabase_http import select


class AdminService:

    def __init__(self, user: dict):
        self.user = user
        self.institution_id = user.get("institution_id")


    # =====================================================
    # 📊 OVERVIEW (INTELLIGENT METRICS)
    # =====================================================
    def get_overview(self):

        users = select("users", "*", {
            "institution_id": self.institution_id
        }) or []

        attempts = select("attempts", "*", {
            "institution_id": self.institution_id
        }) or []

        students = [u for u in users if u.get("role") == "student"]
        teachers = [u for u in users if u.get("role") == "teacher"]

        avg_score = self._calculate_average_score(students)

        return {
            "total_users": len(users),
            "total_students": len(students),
            "total_teachers": len(teachers),
            "total_attempts": len(attempts),
            "average_score": avg_score,
            "performance_level": self._performance_band(avg_score)
        }


    # =====================================================
    # 🧠 TOP STUDENTS (SMART RANKING)
    # =====================================================
    def get_top_students(self):

        students = select("users", "*", {
            "institution_id": self.institution_id,
            "role": "student"
        }) or []

        ranked = sorted(
            students,
            key=lambda x: self._student_score(x),
            reverse=True
        )

        return ranked[:10]


    # =====================================================
    # ⚠️ AT-RISK STUDENTS (INTELLIGENT DETECTION)
    # =====================================================
    def get_at_risk_students(self):

        students = select("users", "*", {
            "institution_id": self.institution_id,
            "role": "student"
        }) or []

        return [
            s for s in students
            if self._student_score(s) < 50
            or s.get("streak", 0) == 0
        ]


    # =====================================================
    # 🧠 HELPER: SAFE SCORE EXTRACTION
    # =====================================================
    def _student_score(self, student: dict) -> float:
        """
        Multi-source scoring (future-proof)
        """
        return float(
            student.get("score")
            or student.get("learning_score")
            or student.get("avg_score")
            or 0
        )


    # =====================================================
    # 📊 HELPER: AVERAGE SCORE
    # =====================================================
    def _calculate_average_score(self, students: list) -> float:

        if not students:
            return 0.0

        scores = [self._student_score(s) for s in students]

        return round(sum(scores) / len(scores), 2)


    # =====================================================
    # 📈 PERFORMANCE CLASSIFICATION
    # =====================================================
    def _performance_band(self, score: float) -> str:

        if score >= 75:
            return "excellent"

        elif score >= 50:
            return "average"

        return "at-risk"