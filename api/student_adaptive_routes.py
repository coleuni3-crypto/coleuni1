from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

from core.security import verify_token
from services.adaptive_engine import (
    get_adaptive_content,
    save_student_performance
)

# =====================================================
# 🧠 ADAPTIVE LEARNING ENGINE (V5 CORE SYSTEM)
# =====================================================
router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning V5"])


# =====================================================
# 📦 REQUEST MODEL (HARDENED + VALIDATED)
# =====================================================
class PerformanceModel(BaseModel):
    material_id: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=100)
    weak_topics: Optional[List[str]] = []


# =====================================================
# 🧠 GET ADAPTIVE CONTENT (PERSONALIZED AI LAYER)
# =====================================================
@router.get("/{material_id}")
def adaptive(material_id: str, user=Depends(verify_token)):

    try:
        user_id = user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session"
            )

        result = get_adaptive_content(
            user_id,
            material_id
        )

        if not result:
            return {
                "success": True,
                "status": "no_data",
                "engine": "adaptive-v5-core",
                "material_id": material_id,
                "message": "No adaptive data available yet"
            }

        return {
            "success": True,
            "status": "ready",
            "engine": "adaptive-v5-core",
            "material_id": material_id,
            "data": result
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[ADAPTIVE ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Adaptive engine failed"
        )


# =====================================================
# 📊 SAVE PERFORMANCE (LEARNING LOOP CORE)
# =====================================================
@router.post("/save")
def save_result(data: PerformanceModel, user=Depends(verify_token)):

    try:
        user_id = user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session"
            )

        result = save_student_performance(
            user_id,
            data.material_id,
            data.score,
            data.weak_topics or []
        )

        return {
            "success": True,
            "engine": "adaptive-learning-loop-v5",
            "message": "Performance saved successfully",
            "data": {
                "material_id": data.material_id,
                "score": data.score,
                "weak_topics_count": len(data.weak_topics or [])
            },
            "learning_loop": result
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[SAVE PERFORMANCE ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to save performance"
        )