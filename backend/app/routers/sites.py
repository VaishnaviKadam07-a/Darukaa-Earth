import random
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.geo_utils import polygon_area_hectares, site_to_out

router = APIRouter(prefix="/api/projects/{project_id}/sites", tags=["sites"])


def _get_owned_project(db, project_id, user):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.owner_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=schemas.SiteOut, status_code=201)
def create_site(
    project_id: str,
    payload: schemas.SiteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_project(db, project_id, current_user)

    geom_shape = shape(payload.geometry.model_dump())
    site = models.Site(
        name=payload.name,
        project_id=project_id,
        geom=from_shape(geom_shape, srid=4326),
        area_hectares=polygon_area_hectares(payload.geometry),
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    _seed_mock_metrics(db, site)

    return site_to_out(db, site)


@router.get("", response_model=List[schemas.SiteOut])
def list_sites(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = _get_owned_project(db, project_id, current_user)
    return [site_to_out(db, s) for s in project.sites]


@router.get("/{site_id}/metrics", response_model=List[schemas.SiteMetricOut])
def get_site_metrics(
    project_id: str,
    site_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_project(db, project_id, current_user)
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    metrics = (
        db.query(models.SiteMetric)
        .filter(models.SiteMetric.site_id == site_id)
        .order_by(models.SiteMetric.recorded_at)
        .all()
    )
    return metrics


@router.delete("/{site_id}", status_code=204)
def delete_site(
    project_id: str,
    site_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_project(db, project_id, current_user)
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()


def _seed_mock_metrics(db: Session, site: models.Site, months: int = 18):
    """
    Generate a plausible monthly time series for a new site so the analytics
    view has something to show immediately. In a real system this would be
    ingested from satellite imagery / field survey pipelines instead.
    """
    base_carbon = random.uniform(50, 400) * (site.area_hectares or 1)
    base_biodiversity = random.uniform(0.4, 0.85)
    base_ndvi = random.uniform(0.3, 0.7)

    start = datetime.utcnow() - timedelta(days=30 * months)
    for i in range(months):
        recorded_at = start + timedelta(days=30 * i)
        # gentle upward drift + noise, so charts show a believable trend
        drift = i / months
        metric = models.SiteMetric(
            site_id=site.id,
            recorded_at=recorded_at,
            carbon_tons=round(base_carbon * (1 + 0.15 * drift) + random.uniform(-5, 5), 2),
            biodiversity_index=round(
                min(1.0, base_biodiversity * (1 + 0.1 * drift) + random.uniform(-0.03, 0.03)), 3
            ),
            ndvi=round(min(1.0, base_ndvi + 0.1 * drift + random.uniform(-0.02, 0.02)), 3),
        )
        db.add(metric)
    db.commit()
