import asyncio
from app.services.llm_factory import get_llm_client
from app.agents.orchestrator_agent import OrchestratorAgent, PipelineError

NOTE_EXEMPLE = """
Patient: Marie Lambert, née le 14/03/1965, sexe féminin, niveau de compréhension médicale faible.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.
"""

async def main():
    orchestrator = OrchestratorAgent(llm_client=get_llm_client())
    try:
        result = await orchestrator.run(NOTE_EXEMPLE)
        print("=== Nombre d'alertes ===", len(result.patient_record.alerts))
        print("\n=== Résumé personnalisé ===")
        print(result.personalized_summary.overview)
    except PipelineError as e:
        print("Erreur du pipeline :", e)

asyncio.run(main())
