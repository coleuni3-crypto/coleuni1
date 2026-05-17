import os
from openai import OpenAI

from rag.vector_store import search_vectors
from services.student_service import get_student_memory, get_weak_topics
from services.learning_loop import process_learning_event
from services.study_autopilot import (
    generate_study_plan,
    build_daily_schedule,
    exam_risk_analysis
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🤖 CHAT SERVICE
# =====================================================
async def chat(query: str, user: dict):

    if not query:
        return {"error": "Missing query"}

    student_id = user["user_id"]
    institution_id = user["institution_id"]

    memory = get_student_memory(student_id, institution_id)
    weak_topics = get_weak_topics(student_id, institution_id)

    context_data = search_vectors(institution_id, query) or []
    context = "\n".join([c.get("content", "") for c in context_data])

    prompt = f"""
You are ColeUni AI Tutor.

MEMORY:
{memory}

WEAK TOPICS:
{weak_topics}

CONTEXT:
{context}

QUESTION:
{query}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict AI tutor."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = res.choices[0].message.content

    loop_result = process_learning_event(
        student_id=student_id,
        institution_id=institution_id,
        query=query,
        ai_response=answer
    )

    return {
        "answer": answer,
        "learning_loop": loop_result
    }


# =====================================================
# 📊 EXAM PREDICT
# =====================================================
async def exam_predict(topics: list, user: dict):

    return exam_risk_analysis(
        user["user_id"],
        user["institution_id"],
        topics
    )


# =====================================================
# 📅 STUDY PLAN
# =====================================================
async def study_plan(topics: list, user: dict):

    return generate_study_plan(
        user["user_id"],
        user["institution_id"],
        topics
    )


# =====================================================
# 🗓 DAILY SCHEDULE
# =====================================================
async def daily_schedule(topics: list, user: dict):

    return build_daily_schedule(
        user["user_id"],
        user["institution_id"],
        topics
    )