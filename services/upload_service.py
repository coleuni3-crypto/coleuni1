import uuid
import json
from fastapi import UploadFile, HTTPException
from typing import Dict, Any

from core.supabase_http import insert, supabase
from services.pdf_processor import extract_text_from_pdf
from services.ai_notes_service import generate_ai_notes


# =====================================================
# ⚙️ CONFIG
# =====================================================
MAX_FILE_SIZE_MB = 25

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".mp3", ".mp4", ".wav"
}


# =====================================================
# 🔐 VALIDATION HELPERS
# =====================================================
def validate_file_size(file_bytes: bytes):
    size_mb = len(file_bytes) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
        )


def validate_file_type(filename: str):
    filename = filename.lower()

    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )


def safe_json_parse(ai_output: str) -> Dict[str, Any]:
    """
    Ensures AI output is always usable even if model returns broken JSON.
    """
    try:
        return json.loads(ai_output)
    except Exception:
        return {
            "raw_output": ai_output,
            "parse_error": True
        }


# =====================================================
# 🧠 MAIN UPLOAD PIPELINE (HARDENED)
# =====================================================
async def upload_learning_material(
    file: UploadFile,
    user: dict,
    title: str,
    course: str,
    description: str = ""
):

    try:
        # =========================
        # 🔐 CONTEXT CHECK
        # =========================
        institution_id = user.get("institution_id")
        uploader_id = user.get("user_id")
        role = user.get("role")

        if role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only teachers/admins can upload materials"
            )

        if not institution_id:
            raise HTTPException(
                status_code=400,
                detail="Missing institution context"
            )

        # =========================
        # 📄 FILE VALIDATION
        # =========================
        validate_file_type(file.filename)

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )

        validate_file_size(file_bytes)

        # =========================
        # 📦 STORAGE PATH
        # =========================
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        storage_path = f"institution_{institution_id}/{unique_name}"

        # =========================
        # ☁️ UPLOAD TO STORAGE
        # =========================
        storage = supabase.storage.from_("learning-materials")

        upload_res = storage.upload(
            storage_path,
            file_bytes,
            {"content-type": file.content_type}
        )

        if upload_res.error:
            raise HTTPException(
                status_code=500,
                detail="File upload failed"
            )

        file_url = storage.get_public_url(storage_path)

        # =========================
        # 📄 TEXT EXTRACTION
        # =========================
        extracted_text = ""

        if file.filename.lower().endswith(".pdf"):
            try:
                extracted_text = extract_text_from_pdf(file_bytes)
            except Exception as e:
                print("[PDF ERROR]", e)

        if not extracted_text:
            extracted_text = f"{title}\n{course}\n{description}"

        # =========================
        # 🧠 AI PROCESSING
        # =========================
        ai_raw = generate_ai_notes(extracted_text)
        ai_result = safe_json_parse(ai_raw)

        # =========================
        # 💾 SAVE MATERIAL
        # =========================
        material = insert("learning_materials", {
            "title": title,
            "course": course,
            "description": description,
            "file_url": file_url,
            "file_name": file.filename,
            "file_type": file.content_type,
            "institution_id": institution_id,
            "uploaded_by": uploader_id,
            "ai_processed": True
        })

        if not material:
            raise HTTPException(
                status_code=500,
                detail="Failed to save material"
            )

        # =========================
        # 🧠 SAVE AI CONTENT
        # =========================
        insert("learning_content", {
            "material_id": material["id"],
            "notes": ai_result.get("notes", ""),
            "flashcards": ai_result.get("flashcards", []),
            "quiz": ai_result.get("quiz", []),
            "audio_text": ai_result.get("audio_text", "")
        })

        # =========================
        # ✅ RESPONSE
        # =========================
        return {
            "success": True,
            "message": "Upload + AI processing complete",
            "material": {
                "id": material["id"],
                "title": title,
                "course": course,
                "file_url": file_url
            },
            "ai_summary": {
                "notes_generated": bool(ai_result.get("notes")),
                "flashcards_count": len(ai_result.get("flashcards", [])),
                "quiz_count": len(ai_result.get("quiz", [])),
                "audio_ready": bool(ai_result.get("audio_text"))
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[UPLOAD ERROR]", str(e))

        raise HTTPException(
            status_code=500,
            detail="Internal server error during upload processing"
        )


# =====================================================
# 📚 GET MATERIALS (SAFE + CLEAN)
# =====================================================
def get_learning_materials(user: dict):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            return {
                "success": False,
                "message": "Missing institution context",
                "materials": []
            }

        res = supabase.table("learning_materials") \
            .select("*") \
            .eq("institution_id", institution_id) \
            .order("id", desc=True) \
            .execute()

        return {
            "success": True,
            "count": len(res.data or []),
            "materials": res.data or []
        }

    except Exception as e:
        print("[GET MATERIALS ERROR]", e)

        return {
            "success": False,
            "message": "Failed to fetch materials",
            "materials": []
        }