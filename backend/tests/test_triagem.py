from app.models.evolucao import Evolucao
from app.models.prontuario import Prontuario


def _cadastrar_paciente(client, auth_headers, cpf="12345678901", cns="123456789012345"):
    resp = client.post(
        "/api/pacientes",
        json={
            "nome": "Maria Aparecida Souza",
            "cpf": cpf,
            "cns": cns,
            "data_nascimento": "1958-05-12",
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


def _vitais(**overrides):
    payload = {"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0}
    payload.update(overrides)
    return payload


def test_calcular_sem_autenticacao_e_recusado(client):
    resp = client.post("/api/triagem/calcular", json=_vitais())
    assert resp.status_code == 403


def test_calcular_retorna_classificacao_sem_persistir(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post("/api/triagem/calcular", json=_vitais(spo2=89), headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["cor"] == "vermelho"

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=paciente_id).one()
    assert prontuario.classificacao_risco is None


def test_calcular_campos_incompletos_retorna_422(client, auth_headers):
    resp = client.post(
        "/api/triagem/calcular",
        json={"fc": 80, "temp": 36.5, "spo2": 98},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_confirmar_persiste_classificacao_e_atualiza_evolucao(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar",
        json=_vitais(dor=9, queixa="Dor no peito"),
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["cor"] == "vermelho"

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=paciente_id).one()
    assert prontuario.classificacao_risco == "vermelho"
    assert prontuario.pas == 100

    evolucoes = db_session.query(Evolucao).filter_by(prontuario_id=prontuario.id).all()
    tipos = {e.tipo for e in evolucoes}
    assert "Cadastro" in tipos
    assert "Triagem" in tipos


def test_confirmar_paciente_inexistente_retorna_404(client, auth_headers):
    resp = client.post(
        "/api/pacientes/99999/triagem/confirmar", json=_vitais(), headers=auth_headers
    )
    assert resp.status_code == 404


def test_confirmar_ja_triado_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar", json=_vitais(), headers=auth_headers
    )
    resp = client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar", json=_vitais(), headers=auth_headers
    )
    assert resp.status_code == 409
