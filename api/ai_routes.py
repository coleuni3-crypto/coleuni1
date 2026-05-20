from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from core.security import verify_token
from services import ai_service

router = APIRouter(prefix="/ai", tags=["COLEUNI AI ENGINE V4"])


# =====================================================
# 🧠 REQUEST MODELS (STRICT + SAFE)
# =====================================================

class ChatRequest(BaseModel):
    query: str
    context: Optional[str] = "student"
    history: Optional[List[dict]] = []


class TopicRequest(BaseModel):
    topics: List[str]


class MaterialRequest(BaseModel):
    material_id: str


# =====================================================
# 🔥 RESPONSE WRAPPER (STANDARD FORMAT)
# =====================================================

def success(data, message="success"):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def fail(message="error", code=500):
    raise HTTPException(
        status_code=code,
        detail={
            "success": False,
            "message": message
        }
    )


# =====================================================
# 🤖 CHAT ENGINE (COLEUNI AI TUTOR CORE)
# =====================================================

@router.post("/chat")
async def chat(req: ChatRequest, user=Depends(verify_token)):

    try:
        institution_id = user.get("institution_id")
        if not institution_id:
            return fail("Missing institution context", 400)

        result = await ai_service.chat(
            query=req.query,
            user=user,
            context=req.context,
            history=req.history
        )

        return success(result, "chat response generated")

    except Exception as e:
        print("[AI CHAT ERROR]", str(e))
        return fail("AI chat failed")


# =====================================================
# 📊 EXAM PREDICTION ENGINE
# =====================================================

@router.post("/exam-predict")
async def exam_predict(req: TopicRequest, user=Depends(verify_token)):

    try:
        result = await ai_service.exam_predict(
            topics=req.topics,
            user=user
        )

        return success(result, "exam prediction completed")

    except Exception as e:
        print("[AI EXAM PREDICT ERROR]", str(e))
        return fail("exam prediction failed")


# =====================================================
# 📚 STUDY PLAN ENGINE (AI AUTOPILOT)
# =====================================================

@router.post("/study-plan")
async def study_plan(req: TopicRequest, user=Depends(verify_token)):

    try:
        result = await ai_service.study_plan(
            topics=req.topics,
            user=user
        )

        return success(result, "study plan generated")

    except Exception as e:
        print("[AI STUDY PLAN ERROR]", str(e))
        return fail("study plan failed")


# =====================================================
# 🗓 DAILY SCHEDULE ENGINE
# =====================================================

@router.post("/daily-schedule")
async def daily_schedule(req: TopicRequest, user=Depends(verify_token)):

    try:
        result = await ai_service.daily_schedule(
            topics=req.topics,
            user=user
        )

        return success(result, "daily schedule created")

    except Exception as e:
        print("[AI DAILY SCHEDULE ERROR]", str(e))
        return fail("daily schedule failed")


# =====================================================
# 🧠 ADAPTIVE LEARNING ENGINE (CORE DIFFERENTIATOR)
# =====================================================

@router.post("/adaptive-learn")
async def adaptive_learn(req: MaterialRequest, user=Depends(verify_token)):

    try:
        engine = getattr(ai_service, "adaptive_learning_engine", None)

        if not engine:
            return fail("adaptive learning engine not available", 501)

        result = await engine(
            material_id=req.material_id,
            user=user
        )

        return success(result, "adaptive learning generated")

    except Exception as e:
        print("[AI ADAPTIVE ERROR]", str(e))
        return fail("adaptive learning failed")