from db import execute_query


def get_system_analytics(institution_id: str):

    total_interactions = execute_query("""
        SELECT COUNT(*) FROM student_performance
        WHERE institution_id=%s
    """, (institution_id,), fetch=True)[0][0]

    avg_score = execute_query("""
        SELECT COALESCE(AVG(score),0)
        FROM student_performance
        WHERE institution_id=%s
    """, (institution_id,), fetch=True)[0][0]

    weak_topics = execute_query("""
        SELECT topic, AVG(score)
        FROM student_performance
        WHERE institution_id=%s
        GROUP BY topic
        ORDER BY AVG(score) ASC
        LIMIT 5
    """, (institution_id,), fetch=True)

    strong_topics = execute_query("""
        SELECT topic, AVG(score)
        FROM student_performance
        WHERE institution_id=%s
        GROUP BY topic
        ORDER BY AVG(score) DESC
        LIMIT 5
    """, (institution_id,), fetch=True)

    return {
        "total_interactions": total_interactions,
        "average_score": float(avg_score),
        "weak_topics": [{"topic": t[0], "score": float(t[1])} for t in weak_topics],
        "strong_topics": [{"topic": t[0], "score": float(t[1])} for t in strong_topics]
    }


def estimate_cost(institution_id: str):

    usage = execute_query("""
        SELECT COUNT(*) FROM student_performance
        WHERE institution_id=%s
    """, (institution_id,), fetch=True)[0][0]

    cost = usage * 0.002

    return {
        "usage_count": usage,
        "estimated_cost_usd": round(cost, 4)
    }


def get_top_students(institution_id: str):

    rows = execute_query("""
        SELECT student_id, AVG(score)
        FROM student_performance
        WHERE institution_id=%s
        GROUP BY student_id
        ORDER BY AVG(score) DESC
        LIMIT 10
    """, (institution_id,), fetch=True)

    return [{"student_id": r[0], "average_score": round(r[1],2)} for r in rows]


def get_at_risk_students(institution_id: str):

    rows = execute_query("""
        SELECT student_id, AVG(score)
        FROM student_performance
        WHERE institution_id=%s
        GROUP BY student_id
        HAVING AVG(score) < 50
    """, (institution_id,), fetch=True)

    return [{"student_id": r[0], "average_score": round(r[1],2)} for r in rows]