import uuid
from fastapi import UploadFile, HTTPException

from core.supabase_http import insert, supabase

from services.pdf_processor import extract_text_from_pdf
from services.ai_notes_service import generate_ai_notes


# =====================================================
# 🧠 COLEUNI AI UPLOAD + PROCESSING ENGINE v4.3
# =====================================================

MAX_FILE_SIZE_MB = 25


# =====================================================
# 📏 FILE SIZE CHECK
# =====================================================
def validate_file_size(file_bytes: bytes):

    size_mb = len(file_bytes) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
        )


# =====================================================
# 📄 FILE TYPE CHECK
# =====================================================
def validate_file_type(filename: str):

    allowed_extensions = [
        ".pdf",
        ".docx",
        ".pptx",
        ".mp3",
        ".mp4",
        ".wav"
    ]

    filename = filename.lower()

    if not any(filename.endswith(ext) for ext in allowed_extensions):

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )


# =====================================================
# 🧠 MAIN UPLOAD PIPELINE
# =====================================================
async def upload_learning_material(
    file: UploadFile,
    user: dict,
    title: str,
    course: str,
    description: str = ""
):

    try:

        # =================================================
        # 🔐 USER CONTEXT
        # =================================================
        institution_id = user.get("institution_id")
        uploader_id = user.get("user_id")
        role = user.get("role")

        # only lecturers/admins
        if role not in ["teacher", "admin"]:

            raise HTTPException(
                status_code=403,
                detail="Only lecturers/admins can upload materials"
            )

        if not institution_id:

            raise HTTPException(
                status_code=400,
                detail="Missing institution context"
            )

        # =================================================
        # 📄 VALIDATE FILE TYPE
        # =================================================
        validate_file_type(file.filename)

        # =================================================
        # 📥 READ FILE
        # =================================================
        file_bytes = await file.read()

        if not file_bytes:

            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )

        # =================================================
        # 📏 VALIDATE FILE SIZE
        # =================================================
        validate_file_size(file_bytes)

        # =================================================
        # 📦 GENERATE STORAGE PATH
        # =================================================
        unique_name = f"{uuid.uuid4()}_{file.filename}"

        storage_path = (
            f"institution_{institution_id}/{unique_name}"
        )

        # =================================================
        # ☁️ UPLOAD TO SUPABASE STORAGE
        # =================================================
        supabase.storage.from_("learning-materials").upload(
            storage_path,
            file_bytes,
            {
                "content-type": file.content_type
            }
        )

        # =================================================
        # 🔗 GET PUBLIC FILE URL
        # =================================================
        file_url = supabase.storage \
            .from_("learning-materials") \
            .get_public_url(storage_path)

        # =================================================
        # 🧠 AI TEXT EXTRACTION
        # =================================================
        extracted_text = ""

        # PDF extraction
        if file.filename.lower().endswith(".pdf"):

            try:
                extracted_text = extract_text_from_pdf(file_bytes)

            except Exception as e:
                print("[PDF EXTRACTION ERROR]", e)

        # fallback text
        if not extracted_text:

            extracted_text = f"""
            {title}

            {course}

            {description}
            """

        # =================================================
        # 🧠 AI LEARNING ENGINE
        # =================================================
        ai_result = generate_ai_notes(extracted_text)

        # =================================================
        # 💾 SAVE MATERIAL
        # =================================================
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

        # =================================================
        # 🧠 SAVE AI LEARNING CONTENT
        # =================================================
        ai_content = insert("learning_content", {

            "material_id": material["id"],

            "notes": ai_result.get("notes", ""),

            "flashcards": ai_result.get("flashcards", []),

            "quiz": ai_result.get("quiz", []),

            "audio_text": ai_result.get("audio_text", "")
        })

        # =================================================
        # ✅ SUCCESS RESPONSE
        # =================================================
        return {

            "success": True,

            "message": "Upload + AI processing complete",

            "material": {
                "id": material["id"],
                "title": material["title"],
                "course": material["course"],
                "file_url": file_url
            },

            "ai_summary": {

                "notes_generated": bool(
                    ai_result.get("notes")
                ),

                "flashcards_count": len(
                    ai_result.get("flashcards", [])
                ),

                "quiz_count": len(
                    ai_result.get("quiz", [])
                ),

                "audio_ready": bool(
                    ai_result.get("audio_text")
                )
            }
        }

    # =====================================================
    # ⚠️ SAFE ERROR HANDLING
    # =====================================================
    except HTTPException as e:
        raise e

    except Exception as e:

        print("[UPLOAD PIPELINE ERROR]", e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error during upload processing"
        )


# =====================================================
# 📚 GET MATERIALS
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

            "count": len(res.data),

            "materials": res.data
        }

    except Exception as e:

        print("[GET MATERIALS ERROR]", e)

        return {

            "success": False,

            "message": "Failed to fetch materials",

            "materials": []
        }