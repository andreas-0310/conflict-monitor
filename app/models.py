from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    feedbacks = relationship("UserFeedback", back_populates="user")


class ConflictData(Base):
    __tablename__ = "conflict_data"
    __table_args__ = (
        Index('idx_country_admin1', 'country', 'admin1'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False, index=True)
    admin1 = Column(String, nullable=False, index=True)
    population = Column(Float, nullable=True)
    events = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    admin1 = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="feedbacks")
