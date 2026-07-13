from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.colaborador import Colaborador


def _cadastrar(client, headers, matricula="123456", pin="1234", perfil="enfermeiro"):
    return client.post(
        "/api/colaboradores",
        json={"matricula": matricula, "pin": pin, "nome": "Colaborador Teste", "perfil": perfil},
        headers=headers,
    )


def test_cadastro_sem_autenticacao_e_recusado(client):
    # HTTPBearer retorna 403 quando falta o header Authorization (comportamento
    # padrao do FastAPI para essa security scheme); token presente mas invalido
    # e coberto por test_token_invalido_retorna_401 em test_rbac.py.
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "777777", "pin": "1234", "nome": "Sem Auth", "perfil": "medico"},
    )
    assert resp.status_code == 403


def test_cadastro_colaborador_nao_expoe_pin(client, auth_headers):
    resp = _cadastrar(client, auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "pin" not in body
    assert "pin_hash" not in body


def test_pin_persistido_apenas_como_hash(client, auth_headers, db_session):
    _cadastrar(client, auth_headers, matricula="222222", pin="4321")

    colaborador = db_session.query(Colaborador).filter_by(matricula="222222").one()
    assert colaborador.pin_hash != "4321"
    assert colaborador.pin_hash.startswith("$2b$")


def test_login_sucesso_retorna_jwt(client, auth_headers):
    _cadastrar(client, auth_headers, matricula="333333", pin="1111", perfil="medico")

    resp = client.post("/api/auth/login", json={"matricula": "333333", "pin": "1111"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_pin_incorreto_retorna_401(client, auth_headers):
    _cadastrar(client, auth_headers, matricula="444444", pin="1111")

    resp = client.post("/api/auth/login", json={"matricula": "444444", "pin": "9999"})
    assert resp.status_code == 401
    assert "access_token" not in resp.json()


def test_login_matricula_inexistente_retorna_401(client):
    resp = client.post("/api/auth/login", json={"matricula": "999999", "pin": "0000"})
    assert resp.status_code == 401


def test_login_colaborador_desligado_retorna_401(client, auth_headers, db_session):
    _cadastrar(client, auth_headers, matricula="888888", pin="1234")
    colaborador = db_session.query(Colaborador).filter_by(matricula="888888").one()
    colaborador.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    resp = client.post("/api/auth/login", json={"matricula": "888888", "pin": "1234"})
    assert resp.status_code == 401


def test_cadastro_matricula_duplicada_retorna_409(client, auth_headers):
    _cadastrar(client, auth_headers, matricula="555555", pin="1234")
    resp = _cadastrar(client, auth_headers, matricula="555555", pin="5678")
    assert resp.status_code == 409


def test_cadastro_race_condicao_retorna_409(client, auth_headers, monkeypatch):
    def commit_com_violacao_unique(self):
        raise IntegrityError("INSERT", {}, Exception("unique constraint failed"))

    monkeypatch.setattr(Session, "commit", commit_com_violacao_unique)

    resp = _cadastrar(client, auth_headers, matricula="666666", pin="1234")
    assert resp.status_code == 409


def test_cadastro_matricula_com_formato_invalido_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "12345", "pin": "1234", "nome": "Teste", "perfil": "medico"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_cadastro_pin_com_formato_invalido_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "123123", "pin": "12a4", "nome": "Teste", "perfil": "medico"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_cadastro_perfil_invalido_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "123123", "pin": "1234", "nome": "Teste", "perfil": "admin"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
