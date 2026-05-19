import os
import json
from openai import OpenAI
from datetime import datetime
from core.supabase_http import insert, select

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# 🧠 SAFE JSON PARSER
# =====================================================
def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        return {
            "summary": text,
            "key_points": [],
            "flashcards": [],
            "quiz": [],
            "syllabus_importance": "unknown",
            "difficulty_level": "medium",
            "student_struggle_areas": [],
            "revision_notes": ""
        }

# =====================================================
# 📤 UPLOAD ENGINE
# =====================================================
async def upload_learning_material(file, user, title, course, description=""):

    try:
        institution_id = user["institution_id"]
        teacher_id = user["user_id"]

        content_bytes = await file.read()

        try:
            file_text = content_bytes.decode("utf-8", errors="ignore")
        except:
            file_text = "Binary file uploaded"

        file_text = file_text[:12000]

        # =================================================
        # 🧠 AI PROMPT
        # =================================================
        prompt = f"""
Convert this lecture into structured JSON ONLY:

{{
  "summary": "...",
  "key_points": [],
  "flashcards": [{{"question": "", "answer": ""}}],
  "quiz": [{{"question": "", "options": [], "answer": ""}}],
  "syllabus_importance": "",
  "difficulty_level": "easy|medium|hard",
  "student_struggle_areas": [],
  "revision_notes": ""
}}

TITLE: {title}
COURSE: {course}

CONTENT:
{file_text}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        ai_raw = response.choices[0].message.content
        ai_data = safe_json_parse(ai_raw)

        # =================================================
        # 💾 SAVE MATERIAL
        # =================================================
        record = insert("learning_materials", {
            "title": title,
            "course": course,
            "description": description,
            "file_text": file_text,
            "teacher_id": teacher_id,
            "institution_id": institution_id,
            "created_at": datetime.utcnow().isoformat()
        })

        material_id = record["id"]

        # =================================================
        # 💾 SAVE AI CONTENT
        # =================================================
        insert("learning_content", {
            "material_id": material_id,
            "notes": ai_data.get("summary", ""),
            "flashcards": ai_data.get("flashcards", []),
            "quiz": ai_data.get("quiz", []),
            "audio_text": ai_data.get("revision_notes", "")
        })

        return {
            "success": True,
            "material_id": material_id,
            "content": ai_data   # IMPORTANT for frontend
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# =====================================================
# 📚 GET MATERIALS (FIXED FOR FRONTEND)
# =====================================================
def get_learning_materials(user):

    institution_id = user["institution_id"]

    materials = select(
        "learning_materials",
        "*",
        {"institution_id": institution_id}
    )

    return {
        "materials": materials
    }