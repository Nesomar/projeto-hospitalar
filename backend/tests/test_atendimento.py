from app.core.security import create_access_token, hash_pin
from app.models.colaborador import Colaborador
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


def _triar(client, auth_headers, paciente_id, **vitais):
    payload = {"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0}
    payload.update(vitais)
    client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar", json=payload, headers=auth_headers
    )


def _headers_enfermeiro(db_session):
    enfermeiro = Colaborador(
        matricula="654321", pin_hash=hash_pin("0000"), nome="Enfermeira Ana", perfil="enfermeiro"
    )
    db_session.add(enfermeiro)
    db_session.commit()
    token = create_access_token(subject=enfermeiro.matricula, perfil=enfermeiro.perfil)
    return {"Authorization": f"Bearer {token}"}


def _status_no_painel(client, auth_headers, paciente_id):
    resp = client.get("/api/painel", headers=auth_headers)
    item = next(i for i in resp.json() if i["paciente_id"] == paciente_id)
    return item


# --- iniciar atendimento ---


def test_iniciar_atendimento_bem_sucedido(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Em Atendimento"

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=paciente_id).one()
    tipos = {e.tipo for e in db_session.query(Evolucao).filter_by(prontuario_id=prontuario.id)}
    assert "Início de Atendimento" in tipos


def test_iniciar_atendimento_sem_triagem_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    assert resp.status_code == 409


def test_iniciar_atendimento_duas_vezes_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    assert resp.status_code == 409


def test_iniciar_atendimento_como_enfermeiro_e_recusado(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    headers_enfermeiro = _headers_enfermeiro(db_session)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=headers_enfermeiro
    )
    assert resp.status_code == 403


# --- alta ---


def test_dar_alta_bem_sucedida_some_do_painel(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/alta", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Alta"

    resp = client.get("/api/painel", headers=auth_headers)
    assert all(item["paciente_id"] != paciente_id for item in resp.json())


def test_dar_alta_sem_atendimento_iniciado_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/alta", headers=auth_headers)
    assert resp.status_code == 409


# --- exames complementares ---


def test_solicitar_exames_bem_sucedido_continua_visivel(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/atendimento/exames",
        json={"observacoes": "Hemograma completo"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Aguardando Exames Complementares"

    item = _status_no_painel(client, auth_headers, paciente_id)
    assert item["status"] == "Aguardando Exames Complementares"
    assert item["pode_retomar_atendimento"] is True


def test_solicitar_exames_fora_de_ordem_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/atendimento/exames", json={}, headers=auth_headers
    )
    assert resp.status_code == 409


# --- retomar atendimento ---


def test_retomar_atendimento_bem_sucedido(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    client.post(
        f"/api/pacientes/{paciente_id}/atendimento/exames", json={}, headers=auth_headers
    )

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/retomar", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Em Atendimento"


def test_retomar_atendimento_fora_de_ordem_retorna_409(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)

    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/retomar", headers=auth_headers)
    assert resp.status_code == 409


# --- painel: booleans de ação por status ---


def test_painel_acoes_visiveis_por_status_para_medico(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)

    item = _status_no_painel(client, auth_headers, paciente_id)
    assert item["pode_iniciar_atendimento"] is True
    assert item["pode_dar_alta"] is False
    assert item["pode_solicitar_exames"] is False

    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    item = _status_no_painel(client, auth_headers, paciente_id)
    assert item["pode_iniciar_atendimento"] is False
    assert item["pode_dar_alta"] is True
    assert item["pode_solicitar_exames"] is True


def test_painel_acoes_ocultas_para_enfermeiro(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar(client, auth_headers, paciente_id)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)
    headers_enfermeiro = _headers_enfermeiro(db_session)

    item = _status_no_painel(client, headers_enfermeiro, paciente_id)
    assert item["pode_iniciar_atendimento"] is False
    assert item["pode_dar_alta"] is False
    assert item["pode_solicitar_exames"] is False
    assert item["pode_retomar_atendimento"] is False
