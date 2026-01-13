from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=11, description="Password must be between 6 and 11 characters")
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 11:
            raise ValueError('Password must be no more than 11 characters')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Conflict data schemas
class ConflictDataBase(BaseModel):
    country: str
    admin1: str
    population: Optional[float] = None
    events: int
    score: float

class ConflictDataResponse(ConflictDataBase):
    id: int
    
    class Config:
        from_attributes = True


class CountryAdmin1Response(BaseModel):
    admin1: str
    score: float
    population: Optional[float] = None
    events: int


class CountryDetailResponse(BaseModel):
    country: str
    admin1_details: List[CountryAdmin1Response]


class ConflictDataListResponse(BaseModel):
    items: List[CountryDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RiskScoreResponse(BaseModel):
    country: str
    average_risk_score: float
    calculated_at: datetime


# User feedback schemas
class UserFeedbackCreate(BaseModel):
    feedback_text: str = Field(..., min_length=10, max_length=500)
    
    @field_validator('feedback_text')
    @classmethod
    def validate_feedback_length(cls, v):
        if len(v) < 10:
            raise ValueError('Feedback text must be at least 10 characters')
        if len(v) > 500:
            raise ValueError('Feedback text must be no more than 500 characters')
        return v


class UserFeedbackResponse(BaseModel):
    id: int
    admin1: str
    country: str
    feedback_text: str
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True


# Delete request schema
class ConflictDataDelete(BaseModel):
    country: str
    admin1: str

