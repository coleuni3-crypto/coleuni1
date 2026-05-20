import os
import json
from openai import OpenAI

from rag.vector_store import search_vectors
from services.student_service import (
    get_student_memory,
    get_weak_topics
)
from services.learning_loop import process_learning_event
from services.study_autopilot import (
    generate_study_plan,
    build_daily_schedule,
    exam_risk_analysis
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# =====================================================
# 🧠 CONTEXT BUILDER (V5 NORMALIZED MEMORY LAYER)
# =====================================================
def build_context(memory, weak_topics, rag_context):

    return {
        "memory": memory.get("interactions", []) if isinstance(memory, dict) else [],
        "memory_strength": memory.get("memory_strength", 0) if isinstance(memory, dict) else 0,
        "weak_topics": weak_topics or [],
        "knowledge_context": rag_context or ""
    }


# =====================================================
# 🔐 SAFE OPENAI CALL (V5 - STRICT + STABLE)
# =====================================================
def safe_openai_call(messages, retries: int = 2):

    last_error = None

    for attempt in range(retries):

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # =========================
            # 🧠 STRICT JSON PARSING
            # =========================
            try:
                parsed = json.loads(content)

                if not isinstance(parsed, dict):
                    raise ValueError("Invalid JSON structure")

                return {
                    "success": True,
                    "data": parsed,
                    "format": "json",
                    "attempt": attempt + 1
                }

            except Exception:
                # fallback structured output
                return {
                    "success": True,
                    "data": {
                        "answer": content,
                        "key_concepts": [],
                        "difficulty": "medium",
                        "confidence": 50,
                        "next_step": "",
                        "revision_needed": []
                    },
                    "format": "fallback_text",
                    "attempt": attempt + 1
                }

        except Exception as e:
            last_error = str(e)

    return {
        "success": False,
        "error": last_error,
        "engine": "openai_failed_after_retries"
    }


# =====================================================
# 🤖 CHAT ENGINE (COLEUNI AI BRAIN V5 CORE)
# =====================================================
async def chat(query: str, user: dict):

    if not query:
        return {"success": False, "error": "Missing query"}

    student_id = user.get("user_id")
    institution_id = user.get("institution_id")

    if not student_id or not institution_id:
        return {"success": False, "error": "Invalid user context"}

    # =========================
    # 🧠 PERSONALIZATION LAYER
    # =========================
    memory = get_student_memory(student_id, institution_id)
    weak_topics = get_weak_topics(student_id, institution_id)

    rag_results = search_vectors(institution_id, query) or []

    rag_context = "\n".join(
        r.get("content", "") for r in rag_results if r.get("content")
    )

    context = build_context(memory, weak_topics, rag_context)

    # =========================
    # 🧠 SYSTEM PROMPT (TIGHT CONTROL)
    # =========================
    system_prompt = """
You are ColeUni AI Tutor (V5 Adaptive Brain).

RULES:
- Be simple, structured, and exam-focused
- Personalize using weak topics
- Use provided context only
- Never hallucinate
- ALWAYS return valid JSON

OUTPUT FORMAT:
{
  "answer": "string",
  "key_concepts": ["string"],
  "difficulty": "easy|medium|hard",
  "confidence": number,
  "next_step": "string",
  "revision_needed": ["string"]
}
"""

    user_prompt = f"""
STUDENT CONTEXT:
{json.dumps(context, ensure_ascii=False)}

QUESTION:
{query}
"""

    result = safe_openai_call([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    # =========================
    # 📊 LEARNING LOOP ENGINE
    # =========================
    loop_result = process_learning_event(
        student_id=student_id,
        institution_id=institution_id,
        query=query,
        ai_response=result.get("data", {})
    )

    return {
        "success": True,
        "engine": "coleuni-ai-brain-v5",
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
            "engine": "exam-risk-ai-v5",
            "data": exam_risk_analysis(
                user.get("user_id"),
                user.get("institution_id"),
                topics
            )
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# =====================================================
# 📚 STUDY PLAN ENGINE
# =====================================================
async def study_plan(topics: list, user: dict):

    try:
        return {
            "success": True,
            "engine": "study-planner-v5",
            "plan": generate_study_plan(
                user.get("user_id"),
                user.get("institution_id"),
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
            "engine": "daily-scheduler-v5",
            "schedule": build_daily_schedule(
                user.get("user_id"),
                user.get("institution_id"),
                topics
            )
        }

    except Exception as e:
        return {"success": False, "error": str(e)}