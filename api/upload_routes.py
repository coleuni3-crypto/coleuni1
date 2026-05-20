import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from openai import OpenAI
from core.supabase_http import insert, select

# =====================================================
# 🤖 OPENAI CLIENT (PRODUCTION SAFE)
# =====================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"
MAX_FILE_SIZE_CHARS = 12000


# =====================================================
# 🧠 SAFE JSON PARSER (HARD RESILIENT CORE)
# =====================================================
def safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Prevents system crash if AI returns invalid JSON.
    """
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return {
        "summary": text or "",
        "key_points": [],
        "flashcards": [],
        "quiz": [],
        "revision_notes": "",
        "difficulty": "medium"
    }


# =====================================================
# 📁 FILE VALIDATION (STRICT)
# =====================================================
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def is_valid_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


# =====================================================
# 📄 SAFE FILE READER (ANTI-CRASH + LIMITS)
# =====================================================
async def read_file_safe(file) -> str:
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        return text[:MAX_FILE_SIZE_CHARS]
    except Exception:
        return "UNREADABLE_CONTENT"


# =====================================================
# 🤖 AI CORE ENGINE (STRICT STRUCTURED OUTPUT)
# =====================================================
def generate_ai_content(title: str, course: str, file_text: str) -> Dict[str, Any]:

    prompt = f"""
You are ColeUni AI Learning Engine.

Return STRICT JSON ONLY. No explanation.

Schema:
{{
  "summary": "string",
  "key_points": ["string"],
  "flashcards": [
    {{"question": "string", "answer": "string"}}
  ],
  "quiz": [
    {{
      "question": "string",
      "options": ["A","B","C","D"],
      "answer": "string"
    }}
  ],
  "revision_notes": "string",
  "difficulty": "easy|medium|hard"
}}

TITLE: {title}
COURSE: {course}

CONTENT:
{file_text}
"""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict JSON generator. Output ONLY valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        raw = res.choices[0].message.content
        return safe_json_parse(raw)

    except Exception as e:
        print("[AI ERROR]", str(e))
        return safe_json_parse("")


# =====================================================
# 📤 UPLOAD + AI PIPELINE (V5 CORE ENGINE)
# =====================================================
async def upload_learning_material(
    file,
    user: dict,
    title: str,
    course: str,
    description: str = ""
) -> Dict[str, Any]:

    try:
        institution_id = user.get("institution_id")
        teacher_id = user.get("user_id")

        # =========================
        # 🔐 AUTH VALIDATION
        # =========================
        if not institution_id or not teacher_id:
            return {"success": False, "error": "Invalid user session"}

        # =========================
        # 📁 FILE VALIDATION
        # =========================
        if not file or not getattr(file, "filename", None):
            return {"success": False, "error": "No file uploaded"}

        if not is_valid_file(file.filename):
            return {"success": False, "error": "Unsupported file type"}

        # =========================
        # 📄 READ FILE
        # =========================
        file_text = await read_file_safe(file)

        # =========================
        # 🤖 AI PROCESSING
        # =========================
        ai_data = generate_ai_content(title, course, file_text)

        # =========================
        # 💾 SAVE MATERIAL (SAFE INSERT)
        # =========================
        material = insert("learning_materials", {
            "title": title,
            "course": course,
            "description": description,
            "file_text": file_text,
            "teacher_id": teacher_id,
            "institution_id": institution_id,
            "created_at": datetime.utcnow().isoformat()
        })

        if not material or "id" not in material:
            return {"success": False, "error": "Material save failed"}

        material_id = material["id"]

        # =========================
        # 💾 SAVE AI CONTENT
        # =========================
        insert("learning_content", {
            "material_id": material_id,
            "notes": ai_data.get("summary", ""),
            "flashcards": ai_data.get("flashcards", []),
            "quiz": ai_data.get("quiz", []),
            "audio_text": ai_data.get("revision_notes", "")
        })

        # =========================
        # 🚀 RESPONSE
        # =========================
        return {
            "success": True,
            "material_id": material_id,
            "ai_content": ai_data,
            "engine": "coleuni-upload-v5-core",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print("[UPLOAD ERROR]", str(e))
        return {"success": False, "error": str(e)}


# =====================================================
# 📚 GET MATERIALS (TENANT SAFE)
# =====================================================
def get_learning_materials(user: dict) -> Dict[str, Any]:

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            return {"success": False, "error": "Missing institution_id"}

        materials = select(
            "learning_materials",
            "*",
            {"institution_id": institution_id}
        ) or []

        return {
            "success": True,
            "count": len(materials),
            "materials": materials
        }

    except Exception as e:
        return {"success": False, "error": str(e)}