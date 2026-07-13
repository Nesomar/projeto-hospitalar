from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.api.deps import get_current_colaborador, require_perfil
from app.core.security import JWT_ALGORITHM, create_access_token
from app.core.config import settings
from app.models.colaborador import Colaborador


def _colaborador(perfil: str) -> Colaborador:
    return Colaborador(id=1, matricula="123456", pin_hash="hash", nome="Teste", perfil=perfil)


def test_medico_pode_prescrever():
    checker = require_perfil("medico")
    medico = _colaborador("medico")
    assert checker(medico) is medico


def test_enfermeiro_nao_pode_prescrever():
    checker = require_perfil("medico")
    enfermeiro = _colaborador("enfermeiro")

    with pytest.raises(HTTPException) as exc_info:
        checker(enfermeiro)

    assert exc_info.value.status_code == 403


def test_require_perfil_aceita_multiplos_perfis():
    checker = require_perfil("medico", "enfermeiro")
    assert checker(_colaborador("medico")) is not None
    assert checker(_colaborador("enfermeiro")) is not None


def test_token_invalido_retorna_401(db_session):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-invalido")

    with pytest.raises(HTTPException) as exc_info:
        get_current_colaborador(credentials=credentials, db=db_session)

    assert exc_info.value.status_code == 401


def test_token_expirado_retorna_401(db_session):
    payload = {
        "sub": "123456",
        "perfil": "medico",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token_expirado = jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_expirado)

    with pytest.raises(HTTPException) as exc_info:
        get_current_colaborador(credentials=credentials, db=db_session)

    assert exc_info.value.status_code == 401


def test_access_token_carrega_matricula_e_perfil_corretos():
    token = create_access_token(subject="654321", perfil="enfermeiro")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])

    assert payload["sub"] == "654321"
    assert payload["perfil"] == "enfermeiro"
