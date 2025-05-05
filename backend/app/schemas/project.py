from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from app.schemas.user import User

class ProjectBase(BaseModel):
    title: str
    description: str
    requirements: Optional[Union[str, List[str]]] = None
    budget: Optional[str] = None
    duration: Optional[str] = None
    status: Optional[str] = "open"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectWithOwner(Project):
    owner: User

    class Config:
        from_attributes = True 