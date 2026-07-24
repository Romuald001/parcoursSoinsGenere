from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import extract, validate, personalize, generate_ui, pipeline

app = FastAPI(
    title="Parcours de Soins Généré - API",
    description="Backend orchestrant le pipeline SMA + IDM pour la génération de tableaux de bord patient",
    version="0.1.0",
)

# CORS : nécessaire pour que le frontend (localhost:5173) puisse appeler le backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extract.router, prefix="/api", tags=["Extraction"])
app.include_router(validate.router, prefix="/api", tags=["Validation"])
app.include_router(personalize.router, prefix="/api", tags=["Personnalisation"])
app.include_router(generate_ui.router, prefix="/api", tags=["Génération UI"])
app.include_router(pipeline.router, prefix="/api", tags=["Pipeline complet"])

@app.get("/health")
def health_check():
    """Endpoint de vérification que le serveur est vivant."""
    return {"status": "ok", "service": "parcours-soins-genere-backend"}