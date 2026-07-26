"""Script de bootstrap : crée le tout premier compte administrateur.

Usage : uv run python -m app.scripts.create_admin <email> <password>

Pattern standard des systèmes réels (équivalent de `createsuperuser` de
Django) : le tout premier compte admin ne peut pas être créé via l'API,
puisqu'aucun admin n'existe encore pour l'autoriser. On passe donc par
un script exécuté directement sur le serveur, hors du circuit HTTP."""

import sys

from app.core.security import hash_password
from app.db.database import SessionLocal, init_db
from app.db.models import UserORM


def create_admin(email: str, password: str) -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(UserORM).filter_by(email=email).first():
            print(f"Un compte existe déjà avec l'email {email}.")
            return
        admin = UserORM(email=email, hashed_password=hash_password(password), role="admin")
        db.add(admin)
        db.commit()
        print(f"Compte administrateur créé : {email}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : uv run python -m app.scripts.create_admin <email> <password>")
        sys.exit(1)
    create_admin(sys.argv[1], sys.argv[2])
