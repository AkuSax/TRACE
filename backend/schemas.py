from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema for creating a new analysis job (request)
class AnalysisJobCreate(BaseModel):
    pass # Initially no fields needed from user to create a job

# Base schema for an analysis job (common attributes)
class AnalysisJobBase(BaseModel):
    id: int
    status: str
    created_at: datetime
    results: Optional[str] = None
    owner_id: int

    class Config:
        from_attributes = True

# Complete schema for an analysis job (response)
class AnalysisJob(AnalysisJobBase):
    pass

# Schema for creating a new user (request)
class UserCreate(BaseModel):
    email: str
    password: str

# Base schema for a user (common attributes)
class UserBase(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# Complete schema for a user, including their analysis jobs (response)
class User(UserBase):
    jobs: list[AnalysisJob] = []