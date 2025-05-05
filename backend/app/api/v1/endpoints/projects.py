from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import project as project_crud
from app.crud import user as user_crud
from app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectWithOwner
from app.schemas.user import User
from app.db.session import get_db
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", response_model=List[ProjectWithOwner])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    try:
        projects = project_crud.get_projects(db, skip=skip, limit=limit, search=search)
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=ProjectWithOwner)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        project = project_crud.get_project(db, project_id=project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return project_crud.create_project(db, project=project, owner_id=current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_project = project_crud.get_project(db, project_id=project_id)
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if db_project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return project_crud.update_project(db, project_id=project_id, project=project)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{project_id}", response_model=Dict[str, Any])
async def delete_project(
    project_id: int,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_project = project_crud.get_project(db, project_id=project_id)
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if db_project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        if project_crud.delete_project(db, project_id=project_id):
            return {"message": "Project deleted successfully"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 