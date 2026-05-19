from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.security import verify_token
from services.adaptive_engine import get_adaptive_content, save_student_performance

# =====================================================
# 🧠 ADAPTIVE ENGINE ROUTER (V4 FINAL)
# =====================================================
router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])


# =====================================================
# 📦 REQUEST MODEL (SAFE + STRICT)
# =====================================================
class PerformanceModel(BaseModel):
    material_id: str
    score: float
    weak_topics: list[str] = []


# =====================================================
# 🧠 GET ADAPTIVE CONTENT (CORE PERSONALIZATION ENGINE)
# =====================================================
@router.get("/{material_id}")
def adaptive(material_id: str, user=Depends(verify_token)):

    try:
        result = get_adaptive_content(
            user["user_id"],
            material_id
        )

        return {
            "success": True,
            "engine": "adaptive-v4-core",
            "material_id": material_id,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Adaptive engine failed: {str(e)}"
        )


# =====================================================
# 📊 SAVE QUIZ RESULT (LEARNING LOOP SYSTEM)
# =====================================================
@router.post("/save")
def save_result(data: PerformanceModel, user=Depends(verify_token)):

    try:
        result = save_student_performance(
            user["user_id"],
            data.material_id,
            data.score,
            data.weak_topics
        )

        return {
            "success": True,
            "message": "Performance saved successfully",
            "engine": "adaptive-learning-loop-v4",
            "learning_loop": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save performance: {str(e)}"
        )