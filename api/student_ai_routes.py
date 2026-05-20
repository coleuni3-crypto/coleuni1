from fastapi import APIRouter, Depends, HTTPException, status
from core.security import verify_token
from core.supabase_http import supabase

router = APIRouter(prefix="/student", tags=["Student AI V5"])


# =====================================================
# 📚 GET ALL LEARNING MATERIALS (STUDENT DASHBOARD)
# =====================================================
@router.get("/materials")
def get_materials(user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")

        if not institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing institution context"
            )

        res = supabase.table("learning_materials") \
            .select("*") \
            .eq("institution_id", institution_id) \
            .order("id", desc=True) \
            .execute()

        materials = res.data or []

        return {
            "success": True,
            "engine": "coleuni-student-materials-v5",
            "count": len(materials),
            "materials": [
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "course": m.get("course"),
                    "description": m.get("description"),
                    "file_url": m.get("file_url"),
                    "uploaded_by": m.get("uploaded_by"),
                    "created_at": m.get("created_at")
                }
                for m in materials
            ]
        }

    except Exception as e:
        print("[MATERIALS ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch materials"
        )


# =====================================================
# 🧠 GET AI LEARNING CONTENT (CORE STUDENT ENGINE)
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
        # 📦 FETCH MATERIAL (TENANT SAFE)
        # =================================================
        material_res = supabase.table("learning_materials") \
            .select("*") \
            .eq("id", material_id) \
            .eq("institution_id", institution_id) \
            .execute()

        material = material_res.data[0] if material_res.data else None

        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning material not found"
            )

        # =================================================
        # 🧠 FETCH AI CONTENT
        # =================================================
        ai_res = supabase.table("learning_content") \
            .select("*") \
            .eq("material_id", material_id) \
            .execute()

        ai = ai_res.data[0] if ai_res.data else None

        # =================================================
        # ⚠️ AI NOT READY YET (SAFE FRONTEND FALLBACK)
        # =================================================
        if not ai:
            return {
                "success": True,
                "engine": "coleuni-student-v5",
                "status": "processing",
                "material": {
                    "id": material["id"],
                    "title": material.get("title"),
                    "course": material.get("course"),
                    "description": material.get("description"),
                    "file_url": material.get("file_url")
                },
                "ai": {
                    "notes": "",
                    "flashcards": [],
                    "quiz": [],
                    "audio_text": ""
                }
            }

        # =================================================
        # ✅ READY RESPONSE (FRONTEND OPTIMIZED)
        # =================================================
        return {
            "success": True,
            "engine": "coleuni-student-v5",
            "status": "ready",

            "material": {
                "id": material["id"],
                "title": material.get("title"),
                "course": material.get("course"),
                "description": material.get("description"),
                "file_url": material.get("file_url"),
                "uploaded_by": material.get("uploaded_by"),
                "created_at": material.get("created_at")
            },

            "ai": {
                "notes": ai.get("notes", ""),
                "flashcards": ai.get("flashcards", []),
                "quiz": ai.get("quiz", []),
                "audio_text": ai.get("audio_text", "")
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[LEARN ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to load learning content"
        )