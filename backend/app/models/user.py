from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    bio = Column(Text)
    skills = Column(Text)  # Stored as JSON string
    experience = Column(Text)  # Stored as JSON string
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    likes_given = relationship("Like", foreign_keys="Like.user_id", back_populates="user", cascade="all, delete-orphan")
    likes_received = relationship("Like", foreign_keys="Like.liked_user_id", back_populates="liked_user", cascade="all, delete-orphan")
    matches = relationship("Match", foreign_keys="Match.user_id", back_populates="user", cascade="all, delete-orphan")
    matches_received = relationship("Match", foreign_keys="Match.liked_user_id", back_populates="liked_user", cascade="all, delete-orphan") 