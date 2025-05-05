from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app.crud import like as like_crud
from app.crud import match as match_crud
from app.db.session import get_db
from app.schemas.user import User
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_matches(
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        matches = match_crud.get_user_matches(db, user_id=current_user.id)
        return matches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/potential", response_model=List[Dict[str, Any]])
async def get_potential_matches(
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        potential_matches = match_crud.get_potential_matches(db, user_id=current_user.id)
        return potential_matches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{user_id}", response_model=Dict[str, Any])
async def create_match(
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

        # Check if user is trying to match with themselves
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot match with yourself"
            )

        # Create like
        like = like_crud.create_like(db, user_id=current_user.id, liked_user_id=user_id)

        # Check if it's a mutual like
        mutual_like = like_crud.get_mutual_like(db, user_id=user_id, liked_user_id=current_user.id)
        if mutual_like:
            # Update both likes to be mutual
            like_crud.update_like(db, like_id=like.id, is_mutual=True)
            like_crud.update_like(db, like_id=mutual_like.id, is_mutual=True)

        return {"message": "Like created successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{match_id}/status", response_model=Dict[str, Any])
async def update_match_status(
    match_id: int,
    status: str,
    current_user: User = Depends(user_crud.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        match = match_crud.update_match_status(db, match_id=match_id, status=status)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        return {"message": "Match status updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 