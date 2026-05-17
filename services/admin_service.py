from core.supabase_http import select

class AdminService:

    def __init__(self, user: dict):
        self.user = user
        self.institution_id = user.get("institution_id")

    # =========================
    # OVERVIEW
    # =========================
    def get_overview(self):

        users = select("users", "*", {
            "institution_id": self.institution_id
        })

        attempts = select("attempts", "*", {
            "institution_id": self.institution_id
        })

        return {
            "total_users": len(users),
            "total_attempts": len(attempts)
        }

    # =========================
    # TOP STUDENTS
    # =========================
    def get_top_students(self):

        students = select("users", "*", {
            "institution_id": self.institution_id,
            "role": "student"
        })

        return sorted(students, key=lambda x: x.get("score", 0), reverse=True)[:10]

    # =========================
    # AT RISK STUDENTS
    # =========================
    def get_at_risk_students(self):

        students = select("users", "*", {
            "institution_id": self.institution_id,
            "role": "student"
        })

        return [s for s in students if s.get("score", 0) < 50]