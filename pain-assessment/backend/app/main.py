from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.alerts import router as alerts_router
from app.api.routes.assessment import router as assessment_router
from app.api.routes.assessment_history import router as assessment_history_router
from app.api.routes.auth import router as auth_router
from app.api.routes.baselines import router as baseline_router
from app.api.routes.behavioral_prediction import router as behavioral_prediction_router
from app.api.routes.datasets import router as dataset_router
from app.api.routes.episodes import router as episode_router
from app.api.routes.evaluations import router as evaluation_router
from app.api.routes.facial_prediction import router as facial_prediction_router
from app.api.routes.features import router as feature_router
from app.api.routes.files import router as files_router
from app.api.routes.fusion import router as fusion_router
from app.api.routes.health import router as health_router
from app.api.routes.interventions import router as intervention_router
from app.api.routes.kpis import router as kpi_router
from app.api.routes.model_status import router as model_status_router
from app.api.routes.monitoring import router as monitoring_router
from app.api.routes.patients import router as patients_router
from app.api.routes.physiological_prediction import router as physiological_prediction_router
from app.api.routes.preprocessing import router as preprocessing_router
from app.api.routes.processing_jobs import router as processing_job_router
from app.api.routes.training_data import router as training_data_router
from app.api.routes.vitals import router as vitals_router
from app.api.routes.voice_analysis import router as voice_analysis_router
from app.api.routes.voice_baselines import router as voice_baseline_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for a patient-profile-aware, "
        "customizable, multilingual, and multimodal "
        "AI-based pain assessment system."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router with /api/v1 prefix
api_v1_router = APIRouter(prefix="/api/v1")
all_routers = [
    auth_router,
    health_router,
    patients_router,
    vitals_router,
    kpi_router,
    baseline_router,
    files_router,
    voice_baseline_router,
    voice_analysis_router,
    processing_job_router,
    preprocessing_router,
    feature_router,
    fusion_router,
    monitoring_router,
    assessment_router,
    assessment_history_router,
    intervention_router,
    dataset_router,
    training_data_router,
    facial_prediction_router,
    physiological_prediction_router,
    behavioral_prediction_router,
    model_status_router,
    evaluation_router,
    episode_router,
    alerts_router,
]

for r in all_routers:
    api_v1_router.include_router(r)
    # Also include at root for direct paths
    app.include_router(r)

app.include_router(api_v1_router)


@app.get("/")
def root():
    return {
        "message": "Pain Assessment Backend is running",
        "version": settings.app_version,
        "environment": settings.environment,
    }