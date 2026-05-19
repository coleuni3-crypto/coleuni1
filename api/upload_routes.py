import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

from openai import OpenAI
from core.supabase_http import insert, select

# =====================================================
# 🤖 OPENAI CLIENT (PRODUCTION SAFE)
# =====================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🧠 SAFE JSON PARSER (HARDENED + ROBUST)
# =====================================================
def safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Ensures AI output never breaks system even if malformed.
    """
    try:
        data = json.loads(text)

        if not isinstance(data, dict):
            raise ValueError("Invalid JSON structure")

        return data

    except Exception:
        return {
            "summary": text or "",
            "key_points": [],
            "flashcards": [],
            "quiz": [],
            "revision_notes": "",
            "difficulty": "medium"
        }


# =====================================================
# 🔒 FILE VALIDATION (SECURE + EXTENSIBLE)
# =====================================================
def is_valid_file(filename: str) -> bool:
    allowed_extensions = {".txt", ".pdf", ".docx"}
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


# =====================================================
# 📄 SAFE FILE READER
# =====================================================
async def read_file_safe(file) -> str:
    """
    Prevents crashes from binary or invalid files.
    """
    try:
        content_bytes = await file.read()
        text = content_bytes.decode("utf-8", errors="ignore")
        return text[:12000]  # safety cap for AI
    except Exception:
        return "UNREADABLE_FILE_CONTENT"


# =====================================================
# 📤 UPLOAD + AI PROCESSING ENGINE (V4.1 CORE)
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
            return {
                "success": False,
                "error": "Invalid user session"
            }

        # =========================
        # 📁 FILE VALIDATION
        # =========================
        if file and getattr(file, "filename", None):
            if not is_valid_file(file.filename):
                return {
                    "success": False,
                    "error": "Unsupported file type (txt, pdf, docx only)"
                }

        # =========================
        # 📄 READ FILE
        # =========================
        file_text = await read_file_safe(file)

        # =========================
        # 🤖 AI PROMPT (STRICT MODE)
        # =========================
        prompt = f"""
You are ColeUni AI Education Engine.

Return STRICT JSON ONLY:

{{
  "summary": "...",
  "key_points": ["..."],
  "flashcards": [{{"question": "...", "answer": "..."}}],
  "quiz": [{{"question": "...", "options": ["A","B","C","D"], "answer": "..."}}],
  "revision_notes": "...",
  "difficulty": "easy|medium|hard"
}}

TITLE: {title}
COURSE: {course}

CONTENT:
{file_text}
"""

        # =========================
        # 🤖 OPENAI CALL (STABLE)
        # =========================
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        ai_raw = response.choices[0].message.content
        ai_data = safe_json_parse(ai_raw)

        # =========================
        # 💾 SAVE MATERIAL
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

        if not material:
            return {
                "success": False,
                "error": "Failed to save material"
            }

        material_id = material.get("id")

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
        # 🚀 RESPONSE (CLEAN)
        # =========================
        return {
            "success": True,
            "material_id": material_id,
            "ai_content": ai_data,
            "engine": "coleuni-upload-v4.1",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print("[UPLOAD ERROR]", str(e))
        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# 📚 GET MATERIALS (SAFE STUDENT API)
# =====================================================
def get_learning_materials(user: dict) -> Dict[str, Any]:

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            return {
                "success": False,
                "error": "Missing institution_id"
            }

        materials = select(
            "learning_materials",
            "*",
            {"institution_id": institution_id}
        ) or []

        return {
            "success": True,
            "materials": materials
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }