from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🧠 MASTER ADAPTIVE SCORING (IMPROVED)
# =====================================================
def calculate_mastery(correct: int, attempts: int, decay: float = 0.0):

    """
    Smarter mastery model:
    - prevents division instability
    - allows learning decay (future-ready)
    """

    if attempts <= 0:
        return 0.0

    base = correct / attempts

    # optional decay factor (future spaced learning integration)
    adjusted = base - decay

    return round(max(0.0, min(1.0, adjusted)), 3)


# =====================================================
# 🔁 SPACED REPETITION ENGINE (UPGRADED)
# =====================================================
def next_review_date(mastery: float, streak: int = 0):

    """
    Adaptive spaced repetition:
    more mastery = longer interval
    streak improves retention timing
    """

    now = datetime.utcnow()

    if mastery < 0.3:
        return now + timedelta(days=1)

    elif mastery < 0.6:
        return now + timedelta(days=2 + streak)

    elif mastery < 0.8:
        return now + timedelta(days=4 + streak)

    else:
        return now + timedelta(days=7 + (2 * streak))


# =====================================================
# 🔐 SAFE OPENAI CALL (ROBUST JSON HANDLING)
# =====================================================
def safe_ai_call(prompt: str) -> Dict[str, Any]:

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        content = res.choices[0].message.content

        # try JSON parse
        try:
            parsed = json.loads(content)
            return {
                "success": True,
                "data": parsed,
                "format": "json"
            }

        except Exception:
            return {
                "success": True,
                "data": {
                    "explanation": content,
                    "example": "",
                    "mini_test": [],
                    "recommendation": "Review topic again"
                },
                "format": "fallback"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "engine": "openai_failure"
        }


# =====================================================
# 🧠 ADAPTIVE RESPONSE ENGINE (CORE BRAIN v2)
# =====================================================
def adaptive_ai_response(topic: str, mastery: float, history: List[dict] = None):

    history = history or []

    # =========================
    # 🎯 DYNAMIC DIFFICULTY
    # =========================
    if mastery < 0.4:
        difficulty = "easy"
    elif mastery < 0.7:
        difficulty = "medium"
    else:
        difficulty = "hard"

    # =========================
    # 🧠 CONTEXT-AWARE PROMPT
    # =========================
    prompt = f"""
You are ColeUni AI Tutor V4 (Adaptive Learning Brain).

RULES:
- Return ONLY valid JSON
- Make explanations personalized
- Adjust difficulty strictly

Topic: {topic}
Mastery Level: {mastery}
Difficulty: {difficulty}

Recent Learning History:
{history[-5:]}

OUTPUT FORMAT:
{{
  "explanation": "...",
  "example": "...",
  "mini_test": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ],
  "recommendation": "...",
  "next_step": "..."
}}
"""

    return safe_ai_call(prompt)