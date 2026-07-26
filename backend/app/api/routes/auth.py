from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, model_validator
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_doctor
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.db.models import PatientORM, UserORM
from app.db.repository import get_user_by_identifier

router = APIRouter()


class RegisterDoctorRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterPatientAccountRequest(BaseModel):
    patient_id: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str

    @model_validator(mode="after")
    def check_identifier_provided(self) -> "RegisterPatientAccountRequest":
        if not self.email and not self.phone:
            raise ValueError("Il faut fournir un email ou un numéro de téléphone.")
        return self


class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    patient_id: str | None = None


@router.post("/auth/register-doctor", status_code=201)
def register_doctor(
    payload: RegisterDoctorRequest,
    db: Session = Depends(get_db),
    _admin: UserORM = Depends(require_admin),
):
    if db.query(UserORM).filter_by(email=payload.email).first():
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé.")
    user = UserORM(email=payload.email, hashed_password=hash_password(payload.password), role="doctor")
    db.add(user)
    db.commit()
    return {"message": "Compte médecin créé."}


@router.post("/auth/register-patient-account", status_code=201)
def register_patient_account(
    payload: RegisterPatientAccountRequest,
    db: Session = Depends(get_db),
    _doctor: UserORM = Depends(require_doctor),
):
    """Réservé aux médecins. Le patient se connectera avec l'identifiant
    fourni ici (email ou téléphone) — au moins un des deux est requis."""
    patient = db.query(PatientORM).filter_by(id=payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable.")

    if payload.email and get_user_by_identifier(db, payload.email):
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé.")
    if payload.phone and get_user_by_identifier(db, payload.phone):
        raise HTTPException(status_code=409, detail="Ce numéro est déjà utilisé.")

    user = UserORM(
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role="patient",
        patient_id=patient.id,
    )
    db.add(user)
    db.commit()
    return {"message": "Compte patient créé."}


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db, payload.identifier)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect.")

    token = create_access_token({"sub": user.id, "role": user.role, "patient_id": user.patient_id})
    return TokenResponse(access_token=token, role=user.role, patient_id=user.patient_id)
