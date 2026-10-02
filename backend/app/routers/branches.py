from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=list[schemas.Branch])
def list_branches(db: Session = Depends(get_db)):
    return crud.get_branches(db)


@router.get("/{branch_id}", response_model=schemas.Branch)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = crud.get_branch(db, branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Pobočka nenalezena")
    return branch


@router.post("/", response_model=schemas.Branch, status_code=201)
def create_branch(
    branch: schemas.BranchCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    return crud.create_branch(db, branch)


@router.put("/{branch_id}", response_model=schemas.Branch)
def update_branch(
    branch_id: int,
    branch: schemas.BranchUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    updated = crud.update_branch(db, branch_id, branch)
    if updated is None:
        raise HTTPException(status_code=404, detail="Pobočka nenalezena")
    return updated


@router.delete("/{branch_id}", status_code=204)
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    try:
        if not crud.delete_branch(db, branch_id):
            raise HTTPException(status_code=404, detail="Pobočka nenalezena")
    except crud.DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
