from sqlalchemy.orm import Session
from app.models.like import Like
from app.models.user import User
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError

def create_like(db: Session, user_id: int, liked_user_id: Optional[int] = None, project_id: Optional[int] = None) -> Like:
    if not liked_user_id and not project_id:
        raise ValueError("Either liked_user_id or project_id must be provided")

    try:
        # Check if like already exists
        query = db.query(Like).filter(Like.user_id == user_id)
        if liked_user_id:
            query = query.filter(Like.liked_user_id == liked_user_id)
        if project_id:
            query = query.filter(Like.project_id == project_id)
        
        existing_like = query.first()
        if existing_like:
            return existing_like

        # Create new like
        db_like = Like(
            user_id=user_id,
            liked_user_id=liked_user_id,
            project_id=project_id,
            is_mutual=False
        )
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise Exception(f"Error creating like: {str(e)}")

def get_mutual_like(db: Session, user_id: int, liked_user_id: int) -> Optional[Like]:
    try:
        return db.query(Like).filter(
            Like.user_id == user_id,
            Like.liked_user_id == liked_user_id,
            Like.is_mutual == True
        ).first()
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")

def update_like(db: Session, like_id: int, is_mutual: bool) -> Optional[Like]:
    try:
        db_like = db.query(Like).filter(Like.id == like_id).first()
        if db_like:
            db_like.is_mutual = is_mutual
            db.commit()
            db.refresh(db_like)
        return db_like
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error: {str(e)}")

def get_user_likes(db: Session, user_id: int) -> List[Dict[str, Any]]:
    try:
        likes = db.query(Like).filter(Like.user_id == user_id).all()
        result = []
        for like in likes:
            if like.liked_user_id:
                liked_user = db.query(User).filter(User.id == like.liked_user_id).first()
                if liked_user:
                    result.append({
                        "id": like.id,
                        "is_mutual": like.is_mutual,
                        "created_at": like.created_at,
                        "user": {
                            "id": liked_user.id,
                            "email": liked_user.email,
                            "username": liked_user.username,
                            "full_name": liked_user.full_name,
                            "bio": liked_user.bio,
                            "skills": liked_user.skills,
                            "experience": liked_user.experience,
                            "is_active": liked_user.is_active,
                            "created_at": liked_user.created_at,
                            "updated_at": liked_user.updated_at
                        }
                    })
        return result
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")

def get_user_liked_by(db: Session, user_id: int) -> List[Dict[str, Any]]:
    try:
        likes = db.query(Like).filter(Like.liked_user_id == user_id).all()
        result = []
        for like in likes:
            user = db.query(User).filter(User.id == like.user_id).first()
            if user:
                result.append({
                    "id": like.id,
                    "is_mutual": like.is_mutual,
                    "created_at": like.created_at,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "skills": user.skills,
                        "experience": user.experience,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    }
                })
        return result
    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}") 