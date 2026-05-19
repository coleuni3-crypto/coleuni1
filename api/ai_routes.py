from fastapi import APIRouter, Depends, Request, HTTPException
from core.security import verify_token
from services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Engine"])


# =====================================================
# 🔐 SAFE REQUEST PARSER (PRODUCTION SAFE)
# =====================================================
async def get_body(request: Request):
    try:
        return await request.json()
    except Exception:
        return {}


# =====================================================
# 🤖 CHAT (AI TUTOR CORE ENGINE)
# =====================================================
@router.post("/chat")
async def chat(request: Request, user=Depends(verify_token)):

    body = await get_body(request)

    query = body.get("query")

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query is required"
        )

    try:
        return await ai_service.chat(
            query=query,
            user=user
        )

    except Exception as e:
        print("[AI CHAT ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="AI chat failed"
        )


# =====================================================
# 📊 EXAM PREDICTION ENGINE
# =====================================================
@router.post("/exam-predict")
async def exam_predict(request: Request, user=Depends(verify_token)):

    body = await get_body(request)

    topics = body.get("topics", [])

    if not isinstance(topics, list):
        raise HTTPException(
            status_code=400,
            detail="topics must be a list"
        )

    try:
        return await ai_service.exam_predict(
            topics=topics,
            user=user
        )

    except Exception as e:
        print("[AI EXAM PREDICT ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Exam prediction failed"
        )


# =====================================================
# 📚 STUDY PLAN ENGINE
# =====================================================
@router.post("/study-plan")
async def study_plan(request: Request, user=Depends(verify_token)):

    body = await get_body(request)

    topics = body.get("topics", [])

    try:
        return await ai_service.study_plan(
            topics=topics,
            user=user
        )

    except Exception as e:
        print("[AI STUDY PLAN ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Study plan failed"
        )


# =====================================================
# 🗓 DAILY SCHEDULE ENGINE
# =====================================================
@router.post("/daily-schedule")
async def daily_schedule(request: Request, user=Depends(verify_token)):

    body = await get_body(request)

    topics = body.get("topics", [])

    try:
        return await ai_service.daily_schedule(
            topics=topics,
            user=user
        )

    except Exception as e:
        print("[AI DAILY SCHEDULE ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Daily schedule failed"
        )


# =====================================================
# 🧠 ADAPTIVE LEARNING ENGINE (CORE V4)
# =====================================================
@router.post("/adaptive-learn")
async def adaptive_learn(request: Request, user=Depends(verify_token)):

    body = await get_body(request)

    material_id = body.get("material_id")

    if not material_id:
        raise HTTPException(
            status_code=400,
            detail="material_id is required"
        )

    try:

        # safety check: function must exist
        if not hasattr(ai_service, "adaptive_learning_engine"):
            raise HTTPException(
                status_code=501,
                detail="Adaptive learning engine not implemented"
            )

        return await ai_service.adaptive_learning_engine(
            material_id=material_id,
            user=user
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        print("[ADAPTIVE LEARN ERROR]", str(e))
        raise HTTPException(
            status_code=500,
            detail="Adaptive learning failed"
        )