from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, admin, learning, assessment, certificates
from app.cli import seed_courses_if_needed, seed_admin_if_needed

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and default course tracks/steps/admins are seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_courses_if_needed(db)
        seed_admin_if_needed(db)
    finally:
        db.close()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.APP_NAME,
    description="Secure, production-grade backend for Plus UAE × Vortexen AI Sales Academy.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware with strict allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(learning.router)
app.include_router(assessment.router)
app.include_router(certificates.router)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }

# Serve static assets and main frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
async def serve_index(request: Request):
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Plus UAE × Vortexen AI Sales Academy</h1><p>Frontend file index.html not found.</p>")

# Mount current directory static files for images (Plus UAE.png, Vortexen.png)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
