from fastapi import APIRouter, Depends
from core.security import verify_token
from core.supabase_http import supabase

router = APIRouter(prefix="/student", tags=["Student AI Learning"])


# =====================================================
# 📚 GET AI LEARNING CONTENT
# =====================================================
@router.get("/learning/{material_id}")
def get_learning_content(material_id: int, user=Depends(verify_token)):

    institution_id = user.get("institution_id")

    # =========================
    # GET MATERIAL
    # =========================
    material = supabase.table("learning_materials") \
        .select("*") \
        .eq("id", material_id) \
        .eq("institution_id", institution_id) \
        .single() \
        .execute()

    # =========================
    # GET AI CONTENT
    # =========================
    ai_content = supabase.table("learning_content") \
        .select("*") \
        .eq("material_id", material_id) \
        .single() \
        .execute()

    if not ai_content.data:
        return {
            "success": False,
            "message": "No AI content found"
        }

    return {
        "success": True,
        "material": material.data,
        "ai": ai_content.data
    }