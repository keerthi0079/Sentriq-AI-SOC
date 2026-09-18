from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.events import router as events_router
from app.api.v1.ml import router as ml_router
from app.api.v1.simulation import router as simulation_router
from app.api.v1.ws import router as ws_router
from app.api.v1.investigation import router as investigation_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(ml_router)
api_v1_router.include_router(simulation_router)
api_v1_router.include_router(ws_router)
api_v1_router.include_router(investigation_router)


