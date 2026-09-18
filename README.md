# Darukaa.Earth — Geospatial Carbon & Biodiversity Dashboard

A full-stack platform for managing and visualizing carbon and biodiversity
projects: administrators create projects, draw geographic sites as polygons
on an interactive map, and drill into per-site analytics over time.

## Architecture

```
┌─────────────┐      HTTPS/JSON      ┌──────────────┐      SQL       ┌──────────────┐
│   React SPA │ ───────────────────► │  FastAPI     │ ─────────────► │  PostgreSQL  │
│ Mapbox GL JS│ ◄─────────────────── │  JWT auth    │ ◄───────────── │  + PostGIS   │
│  Chart.js   │                      │  REST API    │                └──────────────┘
└─────────────┘                      └──────────────┘
```

- **Frontend** (`/frontend`): React 18 + Vite. Mapbox GL JS + Mapbox Draw for
  drawing/viewing site polygons; Chart.js for time-series analytics; plain
  `fetch`-style REST calls via Axios, with a JWT stored client-side and
  attached to every request.
- **Backend** (`/backend`): FastAPI, SQLAlchemy + GeoAlchemy2 for PostGIS
  geometry columns, JWT auth (`python-jose` + `passlib`/bcrypt). Site
  creation stores the drawn polygon as native PostGIS geometry and computes
  area server-side using an equal-area reprojection (not raw lat/lng math).
- **Database**: PostgreSQL 16 with the PostGIS extension, installed and run
  natively on the host (no container required).

### Why this stack
- **PostGIS** over storing raw GeoJSON in a text column: lets the database
  do real geometry validation, indexing (GiST), and future spatial queries
  (e.g. "sites within 5km of X") instead of pushing that logic into the app.
- **FastAPI** over Flask/Django: async-friendly, built-in Pydantic
  validation/OpenAPI docs, and a lighter footprint for an API-only backend.
- **Mock analytics data**: the assignment allows any dataset/mocks. Rather
  than wiring a real satellite-imagery pipeline (out of scope for a
  hackathon), each new site is seeded with 18 months of plausible synthetic
  carbon/biodiversity/NDVI time series (`_seed_mock_metrics` in
  `app/routers/sites.py`), documented inline as a stand-in for a real
  ingestion job.

## Database schema

| Table          | Key columns                                                                 |
|----------------|------------------------------------------------------------------------------|
| `users`        | `id` (UUID), `email` (unique), `hashed_password`, `full_name`                |
| `projects`     | `id`, `name`, `description`, `project_type` (carbon/biodiversity), `owner_id` → `users.id` |
| `sites`        | `id`, `name`, `project_id` → `projects.id`, `geom` (PostGIS `POLYGON`, SRID 4326), `area_hectares` |
| `site_metrics` | `id`, `site_id` → `sites.id`, `recorded_at`, `carbon_tons`, `biodiversity_index`, `ndvi` |

Relationships: `User 1—N Project 1—N Site 1—N SiteMetric`. Deleting a
project cascades to its sites and their metrics.

Tables are created automatically on backend startup for local dev
(`Base.metadata.create_all`); for a production setup, replace this with
proper Alembic migrations (`alembic revision --autogenerate`).



**Prerequisites:**
- [PostgreSQL 16](https://www.postgresql.org/download/windows/) — during
  install, use the **Stack Builder** step (launched automatically at the
  end of the PostgreSQL installer) to also install the **PostGIS**
  extension. Remember the password you set for the `postgres` superuser.
- [Python 3.12](https://www.python.org/downloads/windows/) (check "Add
  python.exe to PATH" during install)
- [Node.js 22](https://nodejs.org/en/download) (LTS)
- A free [Mapbox access token](https://account.mapbox.com/) for the map to render

All commands below are **PowerShell**, run from the repo root
(`darukaa-earth\`) unless noted otherwise.

## API overview

| Method | Path                                              | Description                     |
|--------|----------------------------------------------------|----------------------------------|
| POST   | `/api/auth/register`                               | Create a user                   |
| POST   | `/api/auth/login`                                   | OAuth2 password flow → JWT      |
| GET    | `/api/auth/me`                                      | Current user                    |
| GET    | `/api/projects`                                     | List caller's projects          |
| POST   | `/api/projects`                                     | Create a project                |
| GET    | `/api/projects/{id}`                                | Project + its sites (GeoJSON)   |
| POST   | `/api/projects/{id}/sites`                          | Add a site (GeoJSON polygon)    |
| GET    | `/api/projects/{id}/sites/{site_id}/metrics`        | Time-series analytics for a site|

Full interactive docs at `/docs` once the backend is running.

