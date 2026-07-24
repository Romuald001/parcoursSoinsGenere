import asyncio
from app.services.llm_factory import get_llm_client
from app.agents.extractor_agent import ExtractorAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.personalizer_agent import PersonalizerAgent

NOTE_EXEMPLE = """
Patient: Marie Lambert, née le 14/03/1965, sexe féminin, niveau de compréhension médicale faible.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.
"""

async def main():
    llm = get_llm_client()
    extractor = ExtractorAgent(llm_client=llm)
    verifier = VerifierAgent()
    personalizer = PersonalizerAgent(llm_client=llm)

    record = await extractor.run(NOTE_EXEMPLE)
    record = await verifier.run(record)
    summary = await personalizer.run(record)

    print(summary.model_dump_json(indent=2))

asyncio.run(main())
