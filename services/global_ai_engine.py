from datetime import datetime, timedelta
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🧠 MASTER ADAPTIVE SCORING
# =====================================================
def calculate_mastery(correct: int, attempts: int):

    if attempts == 0:
        return 0.0

    return round(correct / attempts, 2)


# =====================================================
# 🔁 SPACED REPETITION SCHEDULER
# =====================================================
def next_review_date(mastery: float):

    if mastery < 0.3:
        return datetime.now() + timedelta(days=1)

    if mastery < 0.7:
        return datetime.now() + timedelta(days=3)

    return datetime.now() + timedelta(days=7)


# =====================================================
# 🧠 ADAPTIVE RESPONSE ENGINE
# =====================================================
def adaptive_ai_response(topic: str, mastery: float):

    difficulty = "easy" if mastery < 0.4 else "medium" if mastery < 0.7 else "hard"

    prompt = f"""
You are ColeUni AI Tutor V3 (Global Adaptive System).

Topic: {topic}
Student Mastery Level: {mastery}
Difficulty Level: {difficulty}

Return JSON:
{{
  "explanation": "...",
  "example": "...",
  "mini_test": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ],
  "recommendation": "..."
}}

Make learning adaptive and personalized.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content