from app.models.evolucao import Evolucao
from app.models.prontuario import Prontuario


def _paciente_payload(**overrides):
    payload = {
        "nome": "Maria Aparecida Souza",
        "cpf": "12345678901",
        "cns": "123456789012345",
        "data_nascimento": "1958-05-12",
        "sexo": "F",
        "telefone": "(81) 99988-7766",
    }
    payload.update(overrides)
    return payload


def test_cadastro_sem_autenticacao_e_recusado(client):
    resp = client.post("/api/pacientes", json=_paciente_payload())
    assert resp.status_code == 403


def test_cadastro_valido_persiste_e_cria_evolucao(client, auth_headers, db_session):
    resp = client.post("/api/pacientes", json=_paciente_payload(), headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["cpf"] == "12345678901"
    assert body["cns"] == "123456789012345"

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=body["id"]).one()
    assert prontuario.classificacao_risco is None

    evolucao = db_session.query(Evolucao).filter_by(prontuario_id=prontuario.id).one()
    assert evolucao.tipo == "Cadastro"
    assert evolucao.responsavel_matricula == "000001"


def test_cadastro_cpf_invalido_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/pacientes", json=_paciente_payload(cpf="123"), headers=auth_headers
    )
    assert resp.status_code == 422


def test_cadastro_cns_invalido_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/pacientes", json=_paciente_payload(cns="123"), headers=auth_headers
    )
    assert resp.status_code == 422


def test_cadastro_nome_curto_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/pacientes", json=_paciente_payload(nome="Ab"), headers=auth_headers
    )
    assert resp.status_code == 422


def test_cadastro_cpf_duplicado_retorna_409(client, auth_headers):
    client.post("/api/pacientes", json=_paciente_payload(), headers=auth_headers)
    resp = client.post(
        "/api/pacientes",
        json=_paciente_payload(cns="999999999999999"),
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_cadastro_cns_duplicado_retorna_409(client, auth_headers):
    client.post("/api/pacientes", json=_paciente_payload(), headers=auth_headers)
    resp = client.post(
        "/api/pacientes",
        json=_paciente_payload(cpf="99999999999"),
        headers=auth_headers,
    )
    assert resp.status_code == 409
