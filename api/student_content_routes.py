from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_token
from core.supabase_http import supabase

router = APIRouter(prefix="/student-content", tags=["Student Content"])

# =====================================================
# 📚 GET AI CONTENT FOR A MATERIAL (FLASHCARDS + QUIZ + NOTES)
# =====================================================
@router.get("/{material_id}")
def get_student_ai_content(material_id: str, user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            raise HTTPException(
                status_code=400,
                detail="Missing institution context"
            )

        # =================================================
        # 🔍 FETCH AI GENERATED CONTENT
        # =================================================
        res = supabase.table("learning_content") \
            .select("*") \
            .eq("material_id", material_id) \
            .single() \
            .execute()

        # =================================================
        # ⚠️ HANDLE EMPTY CONTENT (AI NOT READY YET)
        # =================================================
        if not res.data:
            return {
                "success": False,
                "message": "AI content not ready yet. Try again later."
            }

        content = res.data

        # =================================================
        # 📦 SAFE RESPONSE FORMAT (FRONTEND FRIENDLY)
        # =================================================
        return {
            "success": True,
            "material_id": material_id,

            "notes": content.get("notes", ""),

            "flashcards": content.get("flashcards", []),

            "quiz": content.get("quiz", []),

            "audio_text": content.get("audio_text", ""),

            "meta": {
                "has_flashcards": len(content.get("flashcards", [])) > 0,
                "has_quiz": len(content.get("quiz", [])) > 0,
                "has_notes": bool(content.get("notes"))
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[STUDENT CONTENT ERROR]", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to load student AI content"
        )


# =====================================================
# 📚 OPTIONAL: LIST STUDENT ACCESSIBLE MATERIALS
# (Fallback endpoint if frontend needs it here)
# =====================================================
@router.get("/materials/list")
def list_materials(user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            raise HTTPException(
                status_code=400,
                detail="Missing institution context"
            )

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
        print("[MATERIAL LIST ERROR]", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to load materials"
        )