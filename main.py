from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import os
import sys

# =====================================================
# 🧠 COLEUNI AI SCHOOL OS - V4.5 PRODUCTION CORE
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

app = FastAPI(
    title="ColeUni AI School OS",
    version="4.5.0",
    description="Production-ready Adaptive AI Education OS"
)

# =====================================================
# 🌐 ENV-BASED FRONTEND CONFIG (IMPORTANT FOR RENDER)
# =====================================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

allow_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

if FRONTEND_URL:
    allow_origins.append(FRONTEND_URL)

# =====================================================
# 🌐 CORS CONFIG
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 🧠 SYSTEM REGISTRY
# =====================================================
routers = {}
router_status = {}

# =====================================================
# 🔗 ROBUST ROUTER LOADER
# =====================================================
def load_router(name: str, import_path: str, obj_name: str = "router"):
    try:
        module = importlib.import_module(import_path)
        router = getattr(module, obj_name)

        app.include_router(router)

        routers[name] = True
        router_status[name] = {
            "status": "loaded",
            "path": import_path
        }

        print(f"✅ LOADED: {name}")

    except ModuleNotFoundError as e:
        routers[name] = False
        router_status[name] = {
            "status": "missing_module",
            "path": import_path,
            "error": str(e)
        }
        print(f"❌ MISSING MODULE: {import_path}")

    except AttributeError as e:
        routers[name] = False
        router_status[name] = {
            "status": "missing_router",
            "path": import_path,
            "error": str(e)
        }
        print(f"❌ MISSING ROUTER: {import_path}")

    except Exception as e:
        routers[name] = False
        router_status[name] = {
            "status": "error",
            "path": import_path,
            "error": str(e)
        }
        print(f"❌ ERROR: {name} -> {e}")

# =====================================================
# 🔗 LOAD CORE MODULES
# =====================================================
load_router("auth", "coleuni.api.auth_routes")
load_router("ai", "coleuni.api.ai_routes")
load_router("admin", "coleuni.api.admin_routes")
load_router("dashboard", "coleuni.api.dashboard_routes")
load_router("upload", "coleuni.api.upload_routes")

load_router("student_ai", "coleuni.api.student_ai_routes")
load_router("student_content", "coleuni.api.student_content_routes")
load_router("adaptive", "coleuni.api.student_adaptive_routes")

# =====================================================
# 🚨 SAFE FALLBACK ENDPOINTS
# =====================================================
@app.get("/student/materials")
def student_materials():
    return {"success": True, "materials": []}

@app.get("/student/learn/{material_id}")
def student_learn(material_id: int):
    return {
        "success": True,
        "content": {
            "notes": "System initializing...",
            "flashcards": [],
            "quiz": []
        }
    }

@app.get("/admin/overview")
def admin_overview():
    return {
        "success": True,
        "total_students": 0,
        "performance": 0
    }

@app.get("/admin/weak-topics")
def weak_topics():
    return {"success": True, "data": []}

@app.get("/admin/top-students")
def top_students():
    return {"success": True, "data": []}

@app.get("/admin/activity")
def activity():
    return {"success": True, "data": []}

# =====================================================
# 🧠 SYSTEM HEALTH
# =====================================================
@app.get("/health")
def health():
    loaded = [k for k, v in routers.items() if v]

    return {
        "status": "healthy",
        "version": "4.5.0",
        "routers_loaded": len(loaded),
        "routers_failed": len(routers) - len(loaded),
        "details": router_status
    }

# =====================================================
# 🏠 ROOT
# =====================================================
@app.get("/")
def root():
    return {
        "status": "OK",
        "system": "ColeUni AI OS",
        "version": "4.5.0",
        "architecture": "production-adaptive-ai",
        "router_status": router_status
    }

# =====================================================
# 📘 API INFO
# =====================================================
@app.get("/api-info")
def api_info():
    return {
        "auth": {
            "login": "/auth/login",
            "signup": "/auth/signup"
        },
        "student": {
            "materials": "/student/materials",
            "learn": "/student/learn/{id}"
        },
        "ai": {
            "chat": "/ai/chat",
            "study_plan": "/ai/study-plan",
            "exam_predict": "/ai/exam-predict"
        },
        "admin": {
            "overview": "/admin/overview",
            "weak_topics": "/admin/weak-topics",
            "top_students": "/admin/top-students"
        }
    }