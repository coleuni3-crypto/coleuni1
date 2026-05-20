from fastapi import APIRouter, Depends, HTTPException, status
from core.security import verify_token
from services.student_service import get_learning_material_with_ai

router = APIRouter(
    prefix="/student",
    tags=["Student AI Learning"]
)


# =====================================================
# 📚 GET AI LEARNING CONTENT (V5 CORE CLEAN ARCHITECTURE)
# =====================================================
@router.get("/learning/{material_id}")
def get_learning_content(material_id: int, user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")
        student_id = user.get("user_id")

        # =========================
        # 🔐 VALIDATION LAYER
        # =========================
        if not institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing institution context"
            )

        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student session"
            )

        if not material_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Material ID is required"
            )

        # =========================
        # 🧠 SERVICE LAYER CALL
        # =========================
        result = get_learning_material_with_ai(
            material_id=material_id,
            institution_id=institution_id,
            student_id=student_id
        )

        # =========================
        # ⚠️ NOT FOUND HANDLING
        # =========================
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning material not found"
            )

        # =========================
        # ⚠️ AI NOT READY CASE
        # =========================
        if result.get("ai") is None:
            return {
                "success": True,
                "engine": "coleuni-student-v5",
                "status": "pending_ai_generation",
                "message": "Material exists but AI processing is not complete yet",
                "material": result.get("material"),
                "ai": None
            }

        # =========================
        # ✅ SUCCESS RESPONSE
        # =========================
        return {
            "success": True,
            "engine": "coleuni-student-v5",
            "status": "ready",
            "material": result.get("material"),
            "ai": {
                "notes": result["ai"].get("notes", ""),
                "flashcards": result["ai"].get("flashcards", []),
                "quiz": result["ai"].get("quiz", []),
                "audio_text": result["ai"].get("audio_text", "")
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[STUDENT ROUTES ERROR]", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load learning content"
        )