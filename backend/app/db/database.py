from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models import Base

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Crée les tables si elles n'existent pas. Approche volontairement
    simple (suffisante pour un projet académique) ; un vrai déploiement
    production utiliserait Alembic pour gérer les migrations de schéma."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency FastAPI : fournit une session DB par requête, la ferme ensuite."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
