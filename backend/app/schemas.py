from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, field_validator


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Geometry ----------
class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


# ---------- Sites ----------
class SiteCreate(BaseModel):
    name: str
    geometry: GeoJSONPolygon


class SiteOut(BaseModel):
    id: str
    name: str
    project_id: str
    area_hectares: Optional[float] = None
    geometry: Any  # GeoJSON dict returned from DB
    created_at: datetime

    class Config:
        from_attributes = True


class SiteMetricOut(BaseModel):
    recorded_at: datetime
    carbon_tons: Optional[float] = None
    biodiversity_index: Optional[float] = None
    ndvi: Optional[float] = None

    class Config:
        from_attributes = True


# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "carbon"

    @field_validator("project_type")
    @classmethod
    def validate_type(cls, v):
        if v not in ("carbon", "biodiversity"):
            raise ValueError("project_type must be 'carbon' or 'biodiversity'")
        return v


class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    project_type: str
    created_at: datetime
    sites: List[SiteOut] = []

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    project_type: str
    created_at: datetime
    site_count: int

    class Config:
        from_attributes = True
