"""Test de la dépendance require_admin, sans DB ni réseau :
on lui passe un objet minimal ayant juste l'attribut .role attendu."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.deps import require_admin


def test_require_admin_accepts_admin_role():
    user = SimpleNamespace(role="admin")
    assert require_admin(user) is user


def test_require_admin_rejects_non_admin():
    user = SimpleNamespace(role="doctor")
    with pytest.raises(HTTPException):
        require_admin(user)
