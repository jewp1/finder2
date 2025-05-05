from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import List, Dict, Any, Optional
import json

def create_project(db: Session, project: ProjectCreate, owner_id: int) -> Project:
    # Convert requirements to JSON string if it's a list
    requirements = project.requirements
    if isinstance(requirements, list):
        requirements = json.dumps(requirements)

    db_project = Project(
        title=project.title,
        description=project.description,
        requirements=requirements,
        budget=project.budget,
        duration=project.duration,
        status=project.status,
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).options(joinedload(Project.owner)).filter(Project.id == project_id).first()

def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Project]:
    query = db.query(Project).options(joinedload(Project.owner))
    if search:
        query = query.filter(
            Project.title.ilike(f"%{search}%") |
            Project.description.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()

def update_project(
    db: Session,
    project_id: int,
    project: ProjectUpdate
) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if db_project:
        update_data = project.dict(exclude_unset=True)
        
        # Convert requirements to JSON string if it's a list
        if 'requirements' in update_data and isinstance(update_data['requirements'], list):
            update_data['requirements'] = json.dumps(update_data['requirements'])
        
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def get_user_projects(db: Session, user_id: int) -> List[Project]:
    return db.query(Project).options(joinedload(Project.owner)).filter(Project.owner_id == user_id).all() 