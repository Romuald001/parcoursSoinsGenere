from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.database import get_db
from app.db.models import UserORM

router = APIRouter()


@router.get("/admin/doctors")
def list_doctors(db: Session = Depends(get_db), _admin: UserORM = Depends(require_admin)):
    """Réservé aux administrateurs : liste des médecins provisionnés."""
    doctors = db.query(UserORM).filter_by(role="doctor").order_by(UserORM.created_at).all()
    return [
        {"id": d.id, "email": d.email, "created_at": d.created_at.isoformat()}
        for d in doctors
    ]
