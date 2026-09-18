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

## Local setup (Windows, no Docker)

This project runs entirely with native tooling — PostgreSQL/PostGIS
installed directly on Windows, a Python virtual environment for the
backend, and Node.js for the frontend. No Docker is required for local
development or for deployment.

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

### 1. Create the PostgreSQL role and database

Open PowerShell and connect with `psql` (installed alongside PostgreSQL,
usually at `C:\Program Files\PostgreSQL\16\bin`). If `psql` isn't on your
PATH, either add that folder to PATH or call it by full path.

```powershell
# Connect as the postgres superuser (it will prompt for the password you set at install time)
psql -U postgres

# Inside the psql prompt, run:
CREATE USER darukaa WITH PASSWORD 'darukaa';
CREATE DATABASE darukaa OWNER darukaa;
\c darukaa
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

If you'd rather not open an interactive `psql` session, you can run the
same steps non-interactively:

```powershell
psql -U postgres -c "CREATE USER darukaa WITH PASSWORD 'darukaa';"
psql -U postgres -c "CREATE DATABASE darukaa OWNER darukaa;"
psql -U postgres -d darukaa -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

Verify PostGIS is active:
```powershell
psql -U darukaa -d darukaa -c "SELECT PostGIS_Version();"
```

### 2. Backend — Python virtual environment and dependencies

```powershell
cd backend

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# If PowerShell blocks the activation script, run this once (as Administrator
# or for the current user) and re-open your terminal:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 3. Backend — configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `backend\.env` and confirm/edit:
```
DATABASE_URL=postgresql://darukaa:darukaa@localhost:5432/darukaa
SECRET_KEY=change-this-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Create the database tables

Tables are created automatically the first time the app starts up
(`Base.metadata.create_all` in `app/main.py`), so simply starting the
backend (next step) will create every table (`users`, `projects`, `sites`,
`site_metrics`) against your local `darukaa` database — no separate
migration command needed for local dev. If you'd rather trigger it without
starting the server:

```powershell
python -c "from app.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
```

(For production, replace this with Alembic migrations — see "What's not
implemented yet" below.)

### 5. Start the backend

```powershell
uvicorn app.main:app --reload
```
Backend is now running at http://localhost:8000 (interactive docs at
http://localhost:8000/docs). Keep this terminal open.

### 6. Frontend — install dependencies and configure environment

Open a **new** PowerShell window:

```powershell
cd frontend
npm install

Copy-Item .env.example .env
```

Open `frontend\.env` and set:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_access_token_here
```

### 7. Start the frontend

```powershell
npm run dev
```
Frontend is now running at http://localhost:5173.

### Running the test suite / lint locally

```powershell
# Backend (from backend\, with venv activated, and DATABASE_URL pointing at
# a real Postgres — a local `darukaa` or `darukaa_test` database both work)
pytest -v
ruff check .
black --check .

# Frontend (from frontend\)
npm run lint
npm run build
```

### Deploying without Docker

Both services are plain Python/Node apps with no Docker dependency, so
they deploy the same way locally and in production:
- **Backend**: any host that can run `pip install -r requirements.txt` and
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT` against a managed
  Postgres/PostGIS instance (e.g. Render's native Python runtime, as
  already defined in `render.yaml`, or Railway/Fly.io/a VM).
- **Frontend**: any static host that can run `npm install && npm run
  build` and serve the resulting `dist/` folder (Render static site,
  Vercel, Netlify, etc.), with `VITE_API_BASE_URL` pointed at wherever the
  backend ends up.
- Set `DATABASE_URL` on the backend host to your managed Postgres
  connection string (with PostGIS enabled) instead of the local one.

## CI/CD pipeline

Defined in `.github/workflows/ci.yml`, runs on every push/PR to `main`.
Note: this pipeline runs on GitHub's own hosted runners and uses a
GitHub Actions **service container** for Postgres — that's GitHub's CI
infrastructure, not a project-level Docker dependency, so it has no
bearing on local development (which is fully Docker-free, see above).

1. **Backend job**: spins up a `postgis/postgis` service container on the
   runner → installs deps → `ruff check` (lint) → `black --check` (format) →
   `pytest` against the live PostGIS database.
2. **Frontend job**: installs deps → `eslint` → `npm run build` (fails the
   build if the app doesn't compile).

`.github/workflows/deploy.yml` runs after CI succeeds on `main` and (if a
`RENDER_DEPLOY_HOOK_URL` repo variable is set) triggers a Render deploy
hook. In practice, once the repo is connected in Render's/Vercel's
dashboard, they auto-deploy on push to `main` without needing this — the
explicit workflow is there so a passing CI run is required before the
hook fires.

**Deployment target**: `render.yaml` defines a Render Blueprint (Postgres +
PostGIS, FastAPI web service, static frontend build). Import it via
Render's "New > Blueprint" pointed at this repo. The Vercel-equivalent is
just the `frontend` directory as a static Vite build with
`VITE_API_BASE_URL`/`VITE_MAPBOX_TOKEN` env vars set.

## Code quality / pre-commit hooks

Husky + lint-staged run on every commit (`.husky/pre-commit`):
- Frontend: ESLint (`--fix`) + Prettier on staged `.js/.jsx/.json/.css/.md`.
- Backend: `ruff check` + `black --check` across the backend.

Set up locally with:
```bash
npm install   # installs husky at the repo root, wires up .git/hooks
```

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

## What's not implemented yet

- Alembic migrations (schema is created via `create_all` for hackathon speed)
- Multi-user collaboration on a single project (currently one owner per project)
- Real data ingestion pipeline (analytics are seeded mock data, documented above)
- Automated frontend tests (backend has pytest coverage on auth/health; frontend relies on lint + build-passes as the CI gate)
