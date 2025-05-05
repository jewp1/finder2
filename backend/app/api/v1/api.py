from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, likes, matches, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(likes.router, prefix="/likes", tags=["likes"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"]) 