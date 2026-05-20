from fastapi import APIRouter, Depends, HTTPException, status
from core.security import verify_token
from core.supabase_http import supabase

router = APIRouter(
    prefix="/student-content",
    tags=["Student Content"]
)


# =====================================================
# 🔐 INTERNAL SAFE HELPERS
# =====================================================
def _safe_single(res):
    return res.data[0] if res.data else None


def _safe_list(res):
    return res.data if res.data else []


# =====================================================
# 📚 GET AI CONTENT FOR A MATERIAL (V5 PRODUCTION CORE)
# =====================================================
@router.get("/{material_id}")
def get_student_ai_content(material_id: str, user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")
        student_id = user.get("user_id")

        # =========================
        # 🔐 VALIDATION
        # =========================
        if not institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing institution context"
            )

        # =========================
        # 📄 VERIFY MATERIAL ACCESS (TENANT SAFE)
        # =========================
        material_res = supabase.table("learning_materials") \
            .select("*") \
            .eq("id", material_id) \
            .eq("institution_id", institution_id) \
            .execute()

        material = _safe_single(material_res)

        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found or access denied"
            )

        # =========================
        # 🧠 FETCH AI CONTENT
        # =========================
        ai_res = supabase.table("learning_content") \
            .select("*") \
            .eq("material_id", material_id) \
            .execute()

        ai_content = _safe_single(ai_res)

        # =========================
        # ⚠️ AI NOT READY YET (FRONTEND SAFE STATE)
        # =========================
        if not ai_content:
            return {
                "success": True,
                "status": "processing",
                "message": "AI content is still being generated",
                "material": {
                    "id": material["id"],
                    "title": material.get("title"),
                    "course": material.get("course"),
                    "file_url": material.get("file_url")
                },
                "ai": None
            }

        # =========================
        # 📦 NORMALIZED AI RESPONSE
        # =========================
        return {
            "success": True,
            "status": "ready",
            "engine": "coleuni-ai-v5",

            "material": {
                "id": material["id"],
                "title": material.get("title"),
                "course": material.get("course"),
                "description": material.get("description"),
                "file_url": material.get("file_url"),
                "uploaded_by": material.get("uploaded_by")
            },

            "ai": {
                "notes": ai_content.get("notes", ""),
                "flashcards": _safe_list(ai_content.get("flashcards")),
                "quiz": _safe_list(ai_content.get("quiz")),
                "audio_text": ai_content.get("audio_text", "")
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[STUDENT CONTENT ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load AI learning content"
        )


# =====================================================
# 📚 LIST MATERIALS (STUDENT DASHBOARD SUPPORT)
# =====================================================
@router.get("/materials/list")
def list_materials(user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing institution context"
            )

        res = supabase.table("learning_materials") \
            .select("id,title,course,description,file_url,created_at") \
            .eq("institution_id", institution_id) \
            .order("id", desc=True) \
            .execute()

        return {
            "success": True,
            "count": len(res.data or []),
            "materials": _safe_list(res)
        }

    except Exception as e:
        print("[MATERIAL LIST ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load materials"
        )