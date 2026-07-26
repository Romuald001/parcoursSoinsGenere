from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import UserORM

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserORM:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.") from e

    user = db.query(UserORM).filter_by(id=payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")
    return user


def require_doctor(user: UserORM = Depends(get_current_user)) -> UserORM:
    if user.role != "doctor":
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins.")
    return user


def require_admin(user: UserORM = Depends(get_current_user)) -> UserORM:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    return user
