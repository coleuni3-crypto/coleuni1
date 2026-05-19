import os
import json
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
# 🧠 GLOBAL AI ENGINE CONFIG (V4)
# =====================================================
MODEL = "gpt-4o-mini"


# =====================================================
# 🔐 SAFE AI WRAPPER (PRODUCTION READY)
# =====================================================
def safe_openai_call(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4
        )

        content = response.choices[0].message.content

        # try parse JSON (GLOBAL OS STANDARD)
        try:
            return json.loads(content)
        except:
            return {
                "answer": content,
                "format": "raw_text_fallback"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": True
        }


# =====================================================
# 🤖 V4 ADAPTIVE TUTOR ENGINE (GLOBAL OS CORE)
# =====================================================
async def chat(query: str, user: dict):

    if not query:
        return {"success": False, "error": "Missing query"}

    student_id = user["user_id"]
    institution_id = user["institution_id"]

    # =========================
    # 🧠 PERSONALIZATION LAYER
    # =========================
    memory = get_student_memory(student_id, institution_id)
    weak_topics = get_weak_topics(student_id, institution_id)

    context_data = search_vectors(institution_id, query) or []
    context = "\n".join([c.get("content", "") for c in context_data])

    # =========================
    # 🌍 GLOBAL EDUCATION OS PROMPT
    # =========================
    prompt = f"""
You are ColeUni Global Education OS (V4).

Return STRICT JSON ONLY:

{{
  "answer": "...",
  "key_concepts": ["..."],
  "difficulty": "easy | medium | hard",
  "student_feedback": {{
      "understood": true/false,
      "confidence_score": 0-100
  }},
  "next_lesson_suggestion": "...",
  "revision_needed": ["topics"]
}}

STUDENT PROFILE:
{memory}

WEAK AREAS:
{weak_topics}

RELEVANT CONTEXT:
{context}

QUESTION:
{query}
"""

    result = safe_openai_call([
        {
            "role": "system",
            "content": "You are a global adaptive education AI engine."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    # =========================
    # 📊 LEARNING LOOP (V4 INTELLIGENCE FEEDBACK)
    # =========================
    loop_result = process_learning_event(
        student_id=student_id,
        institution_id=institution_id,
        query=query,
        ai_response=result
    )

    return {
        "success": True,
        "data": result,
        "learning_loop": loop_result,
        "engine": "coleuni-v4-global-os"
    }


# =====================================================
# 📊 EXAM PREDICTION ENGINE (GLOBAL RISK AI)
# =====================================================
async def exam_predict(topics: list, user: dict):

    try:
        return {
            "success": True,
            "engine": "v4-risk-ai",
            "data": exam_risk_analysis(
                user["user_id"],
                user["institution_id"],
                topics
            )
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# 📅 STUDY PLAN ENGINE (ADAPTIVE SCHEDULER V4)
# =====================================================
async def study_plan(topics: list, user: dict):

    try:
        return {
            "success": True,
            "engine": "adaptive-study-planner-v4",
            "plan": generate_study_plan(
                user["user_id"],
                user["institution_id"],
                topics
            )
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# 🗓 DAILY LEARNING SCHEDULE ENGINE
# =====================================================
async def daily_schedule(topics: list, user: dict):

    try:
        return {
            "success": True,
            "engine": "daily-learning-os-v4",
            "schedule": build_daily_schedule(
                user["user_id"],
                user["institution_id"],
                topics
            )
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }