from fastapi import APIRouter, Depends
from core.security import verify_token
from services.adaptive_engine import get_adaptive_content, save_student_performance

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])


# =====================================================
# 🧠 GET ADAPTIVE CONTENT STRATEGY
# =====================================================
@router.get("/{material_id}")
def adaptive(material_id: str, user=Depends(verify_token)):

    return get_adaptive_content(
        user["user_id"],
        material_id
    )


# =====================================================
# 📊 SAVE QUIZ RESULT
# =====================================================
@router.post("/save")
def save_result(data: dict, user=Depends(verify_token)):

    return save_student_performance(
        user["user_id"],
        data["material_id"],
        data["score"],
        data.get("weak_topics", [])
    )