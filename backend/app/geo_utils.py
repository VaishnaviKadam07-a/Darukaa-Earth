"""Helpers for converting between GeoJSON <-> WKT/PostGIS geometry."""

import json

import pyproj
from geoalchemy2.shape import to_shape
from shapely.geometry import shape
from shapely.ops import transform

from app import schemas


def geojson_to_wkt(geojson: schemas.GeoJSONPolygon) -> str:
    geom = shape(geojson.model_dump())
    return f"SRID=4326;{geom.wkt}"


def polygon_area_hectares(geojson: schemas.GeoJSONPolygon) -> float:
    """Reproject to an equal-area projection to get a real area estimate."""
    geom = shape(geojson.model_dump())
    project = pyproj.Transformer.from_crs(
        "EPSG:4326", "ESRI:54009", always_xy=True
    ).transform  # world Mollweide, equal-area
    projected = transform(project, geom)
    return round(projected.area / 10_000, 4)  # m^2 -> hectares


def site_to_out(db, site) -> dict:
    shp = to_shape(site.geom)
    return {
        "id": site.id,
        "name": site.name,
        "project_id": site.project_id,
        "area_hectares": site.area_hectares,
        "geometry": json.loads(json.dumps(shp.__geo_interface__)),
        "created_at": site.created_at,
    }
