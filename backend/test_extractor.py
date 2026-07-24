import asyncio
from app.services.llm_factory import get_llm_client
from app.agents.extractor_agent import ExtractorAgent, ExtractionError

NOTE_EXEMPLE = """
Patient: Marie Lambert, née le 14/03/1965, sexe féminin.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.
"""

async def main():
    client = get_llm_client()
    agent = ExtractorAgent(llm_client=client)
    try:
        record = await agent.run(NOTE_EXEMPLE)
        print(record.model_dump_json(indent=2))
    except ExtractionError as e:
        print("Erreur d'extraction :", e)

asyncio.run(main())
