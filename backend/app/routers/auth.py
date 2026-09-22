from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="Tento e-mail je již zaregistrován")

    user = crud.create_user(db, payload.name, payload.email, payload.password)
    token = auth.create_access_token(user.id)
    return schemas.Token(access_token=token, user=user)


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Nesprávný e-mail nebo heslo")

    token = auth.create_access_token(user.id)
    return schemas.Token(access_token=token, user=user)


@router.get("/me", response_model=schemas.User)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
