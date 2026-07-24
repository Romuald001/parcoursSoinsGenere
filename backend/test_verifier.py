import asyncio
from app.services.llm_factory import get_llm_client
from app.agents.extractor_agent import ExtractorAgent
from app.agents.verifier_agent import VerifierAgent

NOTE_EXEMPLE = """
Patient: Marie Lambert, née le 14/03/1965, sexe féminin.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.
"""

async def main():
    extractor = ExtractorAgent(llm_client=get_llm_client())
    verifier = VerifierAgent()

    record = await extractor.run(NOTE_EXEMPLE)
    print("=== AVANT vérification ===")
    print(f"Nombre d'alertes : {len(record.alerts)}")

    record = await verifier.run(record)
    print("\n=== APRÈS vérification ===")
    print(f"Nombre d'alertes : {len(record.alerts)}")
    for alert in record.alerts:
        print(f"- [{alert.severity.value}] {alert.message} (cause: {alert.triggered_by})")

asyncio.run(main())
