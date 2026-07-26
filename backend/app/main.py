from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import extract, validate, personalize, generate_ui, pipeline, patients, auth, admin
from app.db.database import init_db

app = FastAPI(
    title="Parcours de Soins Généré - API",
    description="Backend orchestrant le pipeline SMA + IDM pour la génération de tableaux de bord patient",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Patient-Id"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(extract.router, prefix="/api", tags=["Extraction"])
app.include_router(validate.router, prefix="/api", tags=["Validation"])
app.include_router(personalize.router, prefix="/api", tags=["Personnalisation"])
app.include_router(generate_ui.router, prefix="/api", tags=["Génération UI"])
app.include_router(pipeline.router, prefix="/api", tags=["Pipeline complet"])
app.include_router(patients.router, prefix="/api", tags=["Historique patients"])
app.include_router(auth.router, prefix="/api", tags=["Authentification"])
app.include_router(admin.router, prefix="/api", tags=["Administration"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "parcours-soins-genere-backend"}
