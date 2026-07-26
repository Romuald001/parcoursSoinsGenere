"""Notes médicales synthétiques (fictives) pour les tests.
Aucune donnée réelle de patient n'est utilisée, conformément aux
bonnes pratiques RGPD/éthiques mentionnées dans le rapport."""

DIABETES_NOTE = """
Patient: Marie Lambert, née le 14/03/1965, sexe féminin, niveau de compréhension médicale faible.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.
"""

MOCK_EXTRACTION_JSON = """{
  "patient": {
    "first_name": "Marie",
    "last_name": "Lambert",
    "birth_date": "1965-03-14",
    "gender": "female",
    "health_literacy_level": "low"
  },
  "diagnostics": [
    {"label": "Diabète de type 2", "icd10_code": "E11", "confidence": 0.95, "symptoms": []}
  ],
  "medications": [
    {"name": "Metformine", "dosage": "850mg", "frequency": "2 fois par jour", "confidence": 0.95}
  ],
  "treatment_steps": [],
  "clinical_goals": [
    {"label": "HbA1c", "target_value": 7.0, "current_value": 7.8, "unit": "%"}
  ],
  "appointments": [
    {"label": "Consultation de suivi", "date": "2026-09-15T10:00:00", "location": "Cabinet du Dr Martin"}
  ]
}"""

MOCK_PERSONALIZATION_JSON = """{
  "greeting": "Bonjour Marie,",
  "overview": "Vous avez un diabète de type 2, bien pris en charge.",
  "key_priorities": ["Prendre votre Metformine 2 fois par jour"],
  "simplified_glossary": {"HbA1c": "Un examen qui mesure le sucre dans le sang."}
}"""
