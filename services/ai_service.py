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

MODEL = "gpt-4o-mini"


# =====================================================
# 🔐 SAFE OPENAI CALL (V4 PRODUCTION)
# =====================================================
def safe_openai_call(messages):

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4
        )

        content = response.choices[0].message.content

        # try strict JSON parse
        try:
            data = json.loads(content)

            if not isinstance(data, dict):
                raise ValueError("Invalid JSON structure")

            return {
                "success": True,
                "data": data,
                "format": "json"
            }

        except Exception:
            return {
                "success": True,
                "data": {
                    "answer": content,
                    "key_concepts": [],
                    "difficulty": "medium",
                    "student_feedback": {
                        "understood": False,
                        "confidence_score": 0
                    },
                    "next_lesson_suggestion": "",
                    "revision_needed": []
                },
                "format": "fallback_text"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "engine": "openai_failure"
        }


# =====================================================
# 🤖 ADAPTIVE CHAT ENGINE (CORE)
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
    # 🌍 AI PROMPT
    # =========================
    prompt = f"""
You are ColeUni Adaptive Education OS V4.

Return STRICT JSON ONLY:

{{
  "answer": "...",
  "key_concepts": ["..."],
  "difficulty": "easy | medium | hard",
  "student_feedback": {{
      "understood": false,
      "confidence_score": 0-100
  }},
  "next_lesson_suggestion": "...",
  "revision_needed": ["..."]
}}

STUDENT MEMORY:
{memory}

WEAK TOPICS:
{weak_topics}

CONTEXT:
{context}

QUESTION:
{query}
"""

    result = safe_openai_call([
        {"role": "system", "content": "You are a strict AI tutor. Output ONLY JSON."},
        {"role": "user", "content": prompt}
    ])

    # =========================
    # 📊 LEARNING LOOP
    # =========================
    loop_result = process_learning_event(
        student_id=student_id,
        institution_id=institution_id,
        query=query,
        ai_response=result
    )

    return {
        "success": True,
        "engine": "coleuni-v4-adaptive",
        "response": result,
        "learning_loop": loop_result
    }


# =====================================================
# 📊 EXAM PREDICTION ENGINE
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
        return {"success": False, "error": str(e)}


# =====================================================
# 📅 STUDY PLAN ENGINE
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
        return {"success": False, "error": str(e)}


# =====================================================
# 🗓 DAILY SCHEDULE ENGINE
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
        return {"success": False, "error": str(e)}