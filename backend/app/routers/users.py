from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[schemas.User])
def list_users(
    db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    return crud.get_users(db)


@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return user
