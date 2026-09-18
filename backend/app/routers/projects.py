from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import auth, models, schemas
from app.database import get_db
from app.geo_utils import site_to_out

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = models.Project(
        name=payload.name,
        description=payload.description,
        project_type=payload.project_type,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        created_at=project.created_at,
        sites=[],
    )


@router.get("", response_model=List[schemas.ProjectSummary])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    rows = (
        db.query(models.Project, func.count(models.Site.id).label("site_count"))
        .outerjoin(models.Site)
        .filter(models.Project.owner_id == current_user.id)
        .group_by(models.Project.id)
        .all()
    )
    return [
        schemas.ProjectSummary(
            id=p.id,
            name=p.name,
            description=p.description,
            project_type=p.project_type,
            created_at=p.created_at,
            site_count=count,
        )
        for p, count in rows
    ]


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = (
        db.query(models.Project)
        .options(joinedload(models.Project.sites))
        .filter(models.Project.id == project_id, models.Project.owner_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        created_at=project.created_at,
        sites=[site_to_out(db, s) for s in project.sites],
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.owner_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
