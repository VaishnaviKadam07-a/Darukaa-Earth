from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, projects, sites

# Auto-create tables in dev; use Alembic migrations in production.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Darukaa.Earth API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to the deployed frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sites.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
