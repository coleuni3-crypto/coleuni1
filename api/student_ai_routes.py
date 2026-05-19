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
            "count": len(res.data or []),
            "materials": res.data or [],
            "engine": "student-materials-v4"
        }

    except Exception as e:
        print("[MATERIALS ERROR]", str(e))
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

        # =========================
        # 📦 FETCH AI CONTENT
        # =========================
        res = supabase.table("learning_content") \
            .select("*") \
            .eq("material_id", material_id) \
            .single() \
            .execute()

        # =========================
        # ⏳ AI NOT READY YET (FRONTEND SAFE)
        # =========================
        if not res.data:
            return {
                "success": True,
                "status": "processing",
                "material_id": material_id,
                "message": "AI content is still being generated",
                "notes": "",
                "flashcards": [],
                "quiz": [],
                "audio_text": "",
                "engine": "student-ai-v4"
            }

        content = res.data

        return {
            "success": True,
            "status": "ready",
            "material_id": material_id,
            "notes": content.get("notes", ""),
            "flashcards": content.get("flashcards", []),
            "quiz": content.get("quiz", []),
            "audio_text": content.get("audio_text", ""),
            "engine": "student-ai-v4"
        }

    except Exception as e:
        print("[LEARNING CONTENT ERROR]", str(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to load learning content"
        )