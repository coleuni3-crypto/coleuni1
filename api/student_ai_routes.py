from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_token
from core.supabase_http import supabase

router = APIRouter(prefix="/student", tags=["Student AI"])

# =====================================================
# 📚 GET ALL LEARNING MATERIALS (STUDENT VIEW)
# =====================================================
@router.get("/materials")
def get_materials(user=Depends(verify_token)):

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
        print("[MATERIALS ERROR]", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch materials"
        )


# =====================================================
# 🧠 GET AI LEARNING CONTENT (FLASHCARDS + QUIZ + NOTES)
# =====================================================
@router.get("/learn/{material_id}")
def get_learning_content(material_id: str, user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            raise HTTPException(
                status_code=400,
                detail="Missing institution context"
            )

        # =================================================
        # FETCH AI GENERATED CONTENT
        # =================================================
        res = supabase.table("learning_content") \
            .select("*") \
            .eq("material_id", material_id) \
            .single() \
            .execute()

        if not res.data:
            return {
                "success": False,
                "message": "AI content not ready yet"
            }

        content = res.data

        return {
            "success": True,
            "material_id": material_id,
            "notes": content.get("notes", ""),
            "flashcards": content.get("flashcards", []),
            "quiz": content.get("quiz", []),
            "audio_text": content.get("audio_text", "")
        }

    except Exception as e:
        print("[LEARNING CONTENT ERROR]", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to load learning content"
        )