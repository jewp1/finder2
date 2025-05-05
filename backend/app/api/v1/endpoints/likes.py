from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app.crud import like as like_crud
from app.crud import match as match_crud
from app.db.session import get_db
from app.schemas.user import User
from typing import List, Dict, Any
import traceback

router = APIRouter()

@router.post("/user/{user_id}", response_model=Dict[str, Any])
async def like_user(
    user_id: int,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if user exists
        target_user = user_crud.get_user(db, user_id=user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user is trying to like themselves
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot like yourself"
            )

        # Create like
        try:
            like = like_crud.create_like(db, user_id=current_user.id, liked_user_id=user_id)
        except Exception as e:
            print(f"Error creating like: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating like: {str(e)}"
            )

        # Check if it's a mutual like
        try:
            mutual_like = like_crud.get_mutual_like(db, user_id=user_id, liked_user_id=current_user.id)
            if mutual_like:
                # Update both likes to be mutual
                like_crud.update_like(db, like_id=like.id, is_mutual=True)
                like_crud.update_like(db, like_id=mutual_like.id, is_mutual=True)
        except Exception as e:
            print(f"Error checking mutual like: {str(e)}")
            print(traceback.format_exc())
            # Don't raise here, as the like was already created

        return {"message": "Like created successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/user/likes", response_model=List[Dict[str, Any]])
async def get_user_likes(
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        likes = like_crud.get_user_likes(db, user_id=current_user.id)
        return likes
    except Exception as e:
        print(f"Error getting user likes: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user likes: {str(e)}"
        )

@router.get("/user/liked-by", response_model=List[Dict[str, Any]])
async def get_user_liked_by(
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        likes = like_crud.get_user_liked_by(db, user_id=current_user.id)
        return likes
    except Exception as e:
        print(f"Error getting user liked by: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user liked by: {str(e)}"
        )

@router.post("/project/{project_id}", response_model=Dict[str, Any])
async def like_project(
    project_id: int,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create like for the project
        like = like_crud.create_like(db, user_id=current_user.id, project_id=project_id)
        return {"message": "Project liked successfully", "like_id": like.id}
    except Exception as e:
        print(f"Error liking project: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error liking project: {str(e)}"
        )

@router.get("/matches", response_model=List[Dict[str, Any]])
async def get_matches(
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        matches = like_crud.get_matches(db, user_id=current_user.id)
        return matches
    except Exception as e:
        print(f"Error getting matches: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting matches: {str(e)}"
        ) 