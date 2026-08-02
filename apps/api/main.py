from fastapi import FastAPI

from apps.api.src.health import router as health_router
from apps.api.src.routes.tokens import router as token_router
from apps.common.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.version
)


app.include_router(health_router)
app.include_router(token_router)


@app.get("/")
def root():
    return {
        "name": "SolSniper AI",
        "status": "running",
        "version": settings.version
    }