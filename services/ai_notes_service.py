import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


# =====================================================
# 🧠 SAFE AI CALL (NOT BREAKABLE)
# =====================================================
def safe_ai_generate(messages):

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4
        )

        content = res.choices[0].message.content

        # try structured JSON parsing
        try:
            return {
                "success": True,
                "data": json.loads(content)
            }
        except:
            return {
                "success": True,
                "data": {
                    "notes": content,
                    "flashcards": [],
                    "quiz": [],
                    "audio_text": content
                }
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# 🧠 AI NOTES GENERATOR (V2 - PRODUCTION READY)
# =====================================================
def generate_ai_notes(text: str):

    if not text:
        return {
            "success": False,
            "error": "No input text provided"
        }

    # limit input for cost + safety
    clean_text = text[:6000]

    # =====================================================
    # 🌍 AI PROMPT ENGINE
    # =====================================================
    prompt = f"""
You are ColeUni AI Study Engine.

Convert the material into STRICT JSON ONLY:

{{
  "notes": "clean structured study notes",
  "summary": "short exam-focused summary",
  "key_concepts": ["concept 1", "concept 2", "concept 3"],

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

  "audio_text": "simple spoken explanation for students"
}}

RULES:
- Make it exam-focused
- Keep language simple
- Focus on understanding, not copying text
- Extract real learning concepts

MATERIAL:
{clean_text}
"""

    result = safe_ai_generate([
        {
            "role": "system",
            "content": "You are a strict educational AI that outputs only valid JSON."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    # =====================================================
    # 🔥 FALLBACK (IF AI FAILS)
    # =====================================================
    if not result["success"]:
        return {
            "success": False,
            "notes": "AI generation failed",
            "flashcards": [],
            "quiz": [],
            "audio_text": "",
            "error": result.get("error")
        }

    data = result["data"]

    # =====================================================
    # 🧠 ENSURE SAFE STRUCTURE
    # =====================================================
    return {
        "success": True,
        "notes": data.get("notes", ""),
        "summary": data.get("summary", ""),
        "key_concepts": data.get("key_concepts", []),
        "flashcards": data.get("flashcards", []),
        "quiz": data.get("quiz", []),
        "audio_text": data.get("audio_text", ""),
        "engine": "coleuni-ai-notes-v2"
    }