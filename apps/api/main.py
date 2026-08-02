from fastapi import FastAPI

from apps.api.src.health import router as health_router
from apps.api.src.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.version
)


app.include_router(health_router)


@app.get("/")
def root():
    return {
        "name": "SolSniper AI",
        "status": "running",
        "version": settings.version
    }