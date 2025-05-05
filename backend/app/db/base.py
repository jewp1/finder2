# Import all the models, so that Base has them before being imported by Alembic
from app.db.base_class import Base

# Import all models here in a specific order to avoid circular dependencies
from app.models.user import User
from app.models.project import Project
from app.models.like import Like
from app.models.match import Match

__all__ = [
    "Base",
    "User",
    "Project",
    "Like",
    "Match"
] 