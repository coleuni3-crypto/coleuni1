import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🧠 SAFE AI CALL WRAPPER (PRODUCTION STANDARD)
# =====================================================
def _safe_ai_call(messages, fallback_key="notes"):

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4
        )

        content = res.choices[0].message.content

        # =========================
        # 📊 TRY PARSE JSON
        # =========================
        try:
            data = json.loads(content)

            if not isinstance(data, dict):
                raise ValueError("Invalid structure")

            return {
                "success": True,
                "data": data,
                "format": "json"
            }

        except Exception:
            return {
                "success": True,
                "data": {
                    fallback_key: content
                },
                "format": "fallback"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "engine": "ai_lesson_engine_v2"
        }


# =====================================================
# 🧠 REAL AI LEARNING ENGINE (UPGRADED)
# =====================================================
def generate_ai_lesson(text: str):

    if not text:
        return {
            "success": False,
            "error": "No input text provided"
        }

    prompt = f"""
You are ColeUni AI Tutor Engine V2.

Convert this content into STRICT JSON ONLY:

{{
  "notes": "...",
  "flashcards": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ],
  "quiz": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "..."
    }}
  ],
  "audio_text": "..."
}}

CONTENT:
{text}

Rules:
- Keep explanations simple
- Focus on exam preparation
- Ensure flashcards are short and clear
- Quiz must be MCQ format
"""

    result = _safe_ai_call(
        [
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        fallback_key="notes"
    )

    return {
        "success": True,
        "engine": "ai_lesson_engine_v2",
        "data": result
    }


# =====================================================
# 🧠 STUDENT ADAPTIVE EXPLANATION ENGINE (UPGRADED)
# =====================================================
def explain_difficult_topic(topic: str, level: str = "basic"):

    if not topic:
        return {
            "success": False,
            "error": "Topic is required"
        }

    prompt = f"""
You are ColeUni Adaptive Tutor.

Explain this topic clearly:

TOPIC: {topic}
STUDENT LEVEL: {level}

Return STRICT JSON ONLY:

{{
  "explanation": "...",
  "step_by_step": ["..."],
  "example": "...",
  "quick_summary": "..."
}}

Rules:
- Use simple language
- Adjust difficulty based on level
- Always include an example
"""

    result = _safe_ai_call(
        [
            {"role": "system", "content": "You are a strict JSON tutor engine."},
            {"role": "user", "content": prompt}
        ],
        fallback_key="explanation"
    )

    return {
        "success": True,
        "engine": "adaptive_explainer_v2",
        "data": result
    }