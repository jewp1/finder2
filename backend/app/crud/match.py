from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.user import User
from app.models.project import Project
from app.models.like import Like
from typing import List, Dict, Any, Optional

def create_match(db: Session, user_id: int, liked_user_id: Optional[int] = None, project_id: Optional[int] = None) -> Match:
    if not liked_user_id and not project_id:
        raise ValueError("Either liked_user_id or project_id must be provided")

    db_match = Match(
        user_id=user_id,
        liked_user_id=liked_user_id,
        project_id=project_id,
        status="pending"
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_user_matches(db: Session, user_id: int) -> List[Dict[str, Any]]:
    # Get unique matches by project_id or liked_user_id
    matches = db.query(Match).filter(Match.user_id == user_id).all()
    seen_projects = set()
    seen_users = set()
    result = []
    
    for match in matches:
        if match.liked_user_id and match.liked_user_id not in seen_users:
            liked_user = db.query(User).filter(User.id == match.liked_user_id).first()
            if liked_user:
                seen_users.add(match.liked_user_id)
                result.append({
                    "id": match.id,
                    "status": match.status,
                    "created_at": match.created_at,
                    "user": {
                        "id": liked_user.id,
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
        elif match.project_id and match.project_id not in seen_projects:
            project = db.query(Project).filter(Project.id == match.project_id).first()
            if project:
                seen_projects.add(match.project_id)
                result.append({
                    "id": match.id,
                    "status": match.status,
                    "created_at": match.created_at,
                    "project": {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        "requirements": project.requirements,
                        "budget": project.budget,
                        "duration": project.duration,
                        "status": project.status,
                        "owner_id": project.owner_id,
                        "created_at": project.created_at,
                        "updated_at": project.updated_at
                    }
                })
    return result

def update_match_status(db: Session, match_id: int, status: str) -> Match:
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match:
        db_match.status = status
        db.commit()
        db.refresh(db_match)
    return db_match

def get_potential_matches(db: Session, user_id: int) -> List[Dict[str, Any]]:
    # Get users that haven't been matched with or liked yet
    existing_matches = db.query(Match.liked_user_id).filter(Match.user_id == user_id).all()
    existing_likes = db.query(Like.liked_user_id).filter(Like.user_id == user_id).all()
    
    existing_match_ids = {match[0] for match in existing_matches if match[0] is not None}
    existing_like_ids = {like[0] for like in existing_likes if like[0] is not None}
    
    # Combine both sets of IDs
    excluded_ids = existing_match_ids.union(existing_like_ids)
    
    # Get potential users that haven't been matched or liked
    potential_users = db.query(User).filter(
        User.id != user_id,
        ~User.id.in_(excluded_ids) if excluded_ids else True
    ).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "skills": user.skills,
            "experience": user.experience,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        for user in potential_users
    ] 