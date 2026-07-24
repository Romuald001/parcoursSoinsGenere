from fastapi import APIRouter, HTTPException

from app.agents.orchestrator_agent import OrchestratorAgent, PipelineError
from app.domain.ui_schema.dashboard_schema import DashboardSchema
from app.services.llm_factory import get_llm_client
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema
from pydantic import BaseModel

router = APIRouter()


class PipelineRequest(BaseModel):
    raw_note: str


@router.post("/pipeline/run", response_model=DashboardSchema)
async def run_full_pipeline(payload: PipelineRequest) -> DashboardSchema:
    """Endpoint pratique exécutant le pipeline complet en un seul appel :
    note libre -> extraction -> vérification -> personnalisation -> schéma UI.

    Utile pour les démonstrations et tests rapides. Les 4 endpoints séparés
    (/extract, /validate, /personalize, /generate-ui) restent disponibles
    pour un usage détaillé, notamment la vue "Modèle" éditable du frontend."""
    orchestrator = OrchestratorAgent(llm_client=get_llm_client())
    try:
        result = await orchestrator.run(payload.raw_note)
    except PipelineError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return transform_to_dashboard_schema(result)