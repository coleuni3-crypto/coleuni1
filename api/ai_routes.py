from fastapi import APIRouter, Depends, Request
from core.security import verify_token
from services import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


# =====================================================
# 🤖 CHAT
# =====================================================
@router.post("/chat")
async def chat(
    request: Request,
    user=Depends(verify_token)
):
    body = await request.json()

    return await ai_service.chat(
        query=body.get("query"),
        user=user
    )


# =====================================================
# 📊 EXAM PREDICT
# =====================================================
@router.post("/exam-predict")
async def exam_predict(
    request: Request,
    user=Depends(verify_token)
):
    body = await request.json()

    return await ai_service.exam_predict(
        topics=body.get("topics", []),
        user=user
    )


# =====================================================
# 📚 STUDY PLAN
# =====================================================
@router.post("/study-plan")
async def study_plan(
    request: Request,
    user=Depends(verify_token)
):
    body = await request.json()

    return await ai_service.study_plan(
        topics=body.get("topics", []),
        user=user
    )


# =====================================================
# 🗓 DAILY SCHEDULE
# =====================================================
@router.post("/daily-schedule")
async def daily_schedule(
    request: Request,
    user=Depends(verify_token)
):
    body = await request.json()

    return await ai_service.daily_schedule(
        topics=body.get("topics", []),
        user=user
    )