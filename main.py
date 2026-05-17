from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth_routes import router as auth_router
from api.ai_routes import router as ai_router
from api.admin_routes import router as admin_router
from api.dashboard_routes import router as dashboard_router


app = FastAPI(
    title="ColeUni AI SaaS",
    version="3.2.0",
    description="AI-powered adaptive learning platform"
)

# =====================================================
# CORS (VITE + REACT FIXED)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTES
# =====================================================
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(dashboard_router)


# =====================================================
# ROOT
# =====================================================
@app.get("/")
def root():
    return {
        "status": "OK",
        "service": "ColeUni AI SaaS",
        "version": "3.2.0"
    }


# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "auth": "active",
        "ai": "active",
        "db": "supabase connected"
    }