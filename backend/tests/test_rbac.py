import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import get_current_colaborador, require_perfil
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


def test_token_invalido_retorna_401(db_session):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-invalido")

    with pytest.raises(HTTPException) as exc_info:
        get_current_colaborador(credentials=credentials, db=db_session)

    assert exc_info.value.status_code == 401
