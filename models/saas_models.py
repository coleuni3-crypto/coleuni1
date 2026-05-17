from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =====================================================
# 📊 STUDENT PERFORMANCE MODEL
# =====================================================
class StudentPerformance(BaseModel):

    student_id: str = Field(..., min_length=1)
    institution_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)

    score: float = Field(..., ge=0, le=100)

    created_at: Optional[datetime] = None


# =====================================================
# 🧠 STUDENT MEMORY MODEL
# =====================================================
class StudentMemory(BaseModel):

    student_id: str = Field(..., min_length=1)
    institution_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)

    created_at: Optional[datetime] = None


# =====================================================
# 👤 USER MODEL (FOR FUTURE AUTH SYSTEM)
# =====================================================
class User(BaseModel):

    id: Optional[str] = None
    email: str
    password: Optional[str] = None   # hashed later
    role: str = "student"
    institution_id: str


# =====================================================
# 🏫 INSTITUTION MODEL (MULTI-TENANT CORE)
# =====================================================
class Institution(BaseModel):

    id: Optional[str] = None
    name: str
    created_at: Optional[datetime] = None