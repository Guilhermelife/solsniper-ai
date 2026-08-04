from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.src.health import router as health_router
from apps.api.src.routes.tokens import router as token_router
from apps.api.src.routes.analytics import router as analytics_router
from apps.api.src.routes.runtime import router as runtime_router
from apps.api.src.routes.readiness import router as readiness_router
from apps.api.src.routes.system import router as system_router
from apps.api.src.routes.config import router as config_router
from apps.api.src.routes.logs_api import router as logs_router
from apps.api.src.routes.market_api import router as market_router
from apps.common.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router, prefix="/api")
app.include_router(token_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(runtime_router, prefix="/api")
app.include_router(readiness_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(market_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "SolSniper AI",
        "status": "running",
        "version": settings.version
    }