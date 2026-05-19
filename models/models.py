from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# =====================================================
# 📊 STUDENT PERFORMANCE MODEL (ADAPTIVE CORE)
# =====================================================
class StudentPerformance(BaseModel):

    student_id: str = Field(..., min_length=1)
    institution_id: str = Field(..., min_length=1)
    material_id: Optional[str] = None

    topic: str = Field(..., min_length=1)

    score: float = Field(..., ge=0, le=100)
    weak_topics: Optional[List[str]] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =====================================================
# 🧠 STUDENT MEMORY MODEL (PERSONALIZATION CORE)
# =====================================================
class StudentMemory(BaseModel):

    student_id: str = Field(..., min_length=1)
    institution_id: str = Field(..., min_length=1)

    content: str = Field(..., min_length=1)
    learning_score: float = 0.0

    last_query: Optional[str] = None
    last_activity: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =====================================================
# 👤 USER MODEL (AUTH SYSTEM READY)
# =====================================================
class User(BaseModel):

    id: Optional[str] = None
    email: str = Field(..., min_length=3)
    password: Optional[str] = None   # hashed later

    role: str = Field(default="student")
    institution_id: str

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =====================================================
# 🏫 INSTITUTION MODEL (MULTI-TENANT CORE)
# =====================================================
class Institution(BaseModel):

    id: Optional[str] = None
    name: str = Field(..., min_length=2)

    created_at: datetime = Field(default_factory=datetime.utcnow)