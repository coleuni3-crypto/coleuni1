import os
import json
from datetime import datetime
from openai import OpenAI
from core.supabase_http import insert

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🔐 SAFE JSON PARSER (CRITICAL UPGRADE)
# =====================================================
def safe_json_parse(text: str):
    """
    Prevents AI malformed JSON breaking system
    """
    try:
        return json.loads(text)
    except Exception:
        return {
            "summary": text,
            "key_concepts": [],
            "flashcards": [],
            "quiz": [],
            "importance": "",
            "weak_points": [],
            "raw_ai_output": text
        }


# =====================================================
# 📂 MAIN UPLOAD PROCESSOR (V5 CORE ENGINE)
# =====================================================
async def process_upload(file_text: str, title: str, topic: str, user: dict):

    institution_id = user.get("institution_id")
    teacher_id = user.get("user_id")

    if not institution_id or not teacher_id:
        return {
            "success": False,
            "error": "Missing user context"
        }

    # =================================================
    # 🧠 1. AI EDUCATION ANALYSIS ENGINE
    # =================================================
    prompt = f"""
You are ColeUni AI Education Engine V5.

Analyze this learning material for a school system.

TITLE: {title}
TOPIC: {topic}

CONTENT:
{file_text}

TASKS:
1. Summarize in simple student-friendly language
2. Extract key concepts
3. Create flashcards (Q&A format)
4. Generate 5 exam questions
5. Explain importance in syllabus
6. Identify weak areas students struggle with

RETURN STRICT JSON ONLY:
{{
  "summary": "",
  "key_concepts": [],
  "flashcards": [
    {{"q": "", "a": ""}}
  ],
  "quiz": [
    {{"q": "", "a": ""}}
  ],
  "importance": "",
  "weak_points": []
}}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict education AI that outputs only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        ai_output_raw = res.choices[0].message.content
        ai_output = safe_json_parse(ai_output_raw)

    except Exception as e:
        return {
            "success": False,
            "error": f"AI processing failed: {str(e)}",
            "engine": "upload-v5"
        }

    # =================================================
    # 💾 2. SAVE TO DATABASE (CLEAN STRUCTURE)
    # =================================================
    try:
        record = insert("learning_materials", {
            "title": title,
            "topic": topic,
            "content_raw": file_text[:50000],  # safety limit
            "ai_summary": ai_output.get("summary"),
            "ai_key_concepts": ai_output.get("key_concepts"),
            "ai_flashcards": ai_output.get("flashcards"),
            "ai_quiz": ai_output.get("quiz"),
            "ai_importance": ai_output.get("importance"),
            "ai_weak_points": ai_output.get("weak_points"),
            "teacher_id": teacher_id,
            "institution_id": institution_id,
            "created_at": datetime.utcnow().isoformat(),
            "engine_version": "coleuni-upload-v5"
        })

    except Exception as e:
        return {
            "success": False,
            "error": f"Database insert failed: {str(e)}"
        }

    # =================================================
    # 📊 3. RESPONSE (FRONTEND READY)
    # =================================================
    return {
        "success": True,
        "message": "AI processing complete",
        "material_id": record.get("id"),
        "ai": ai_output,
        "meta": {
            "title": title,
            "topic": topic,
            "teacher_id": teacher_id,
            "institution_id": institution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "engine": "coleuni-upload-v5"
        }
    }