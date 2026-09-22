from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import auth, crud, models
from .database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Přihlášení je vyžadováno")

    user_id = auth.decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Neplatný nebo vypršelý token")

    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Uživatel nenalezen")
    return user


def require_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Vyžadována jsou práva administrátora")
    return current_user
