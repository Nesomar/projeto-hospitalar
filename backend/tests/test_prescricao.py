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


def _headers_enfermeiro(db_session):
    enfermeiro = Colaborador(
        matricula="654321", pin_hash=hash_pin("0000"), nome="Enfermeira Ana", perfil="enfermeiro"
    )
    db_session.add(enfermeiro)
    db_session.commit()
    token = create_access_token(subject=enfermeiro.matricula, perfil=enfermeiro.perfil)
    return {"Authorization": f"Bearer {token}"}


def test_prescrever_sem_autenticacao_e_recusado(client):
    resp = client.post(
        "/api/pacientes/1/prescricoes", json={"medicamento": "Dipirona", "dosagem": "500mg"}
    )
    assert resp.status_code == 403


def test_prescrever_como_enfermeiro_e_recusado(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    headers_enfermeiro = _headers_enfermeiro(db_session)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=headers_enfermeiro,
    )
    assert resp.status_code == 403


def test_prescrever_paciente_inexistente_retorna_404(client, auth_headers):
    resp = client.post(
        "/api/pacientes/99999/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_prescrever_sem_medicamento_ou_dosagem_retorna_422(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"medicamento": "", "dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 422

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_prescrever_via_invalida_retorna_422(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg", "via": "Nasal"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_prescrever_persiste_e_cria_evolucao(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={
            "medicamento": "Dipirona",
            "dosagem": "500mg",
            "via": "IV",
            "frequencia": "8/8h",
            "observacoes": "Se dor",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["medicamento"] == "Dipirona"
    assert corpo["via"] == "IV"
    assert corpo["responsavel_matricula"] == "000001"

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=paciente_id).one()
    evolucoes = db_session.query(Evolucao).filter_by(prontuario_id=prontuario.id).all()
    tipos = {e.tipo for e in evolucoes}
    assert "Prescrição" in tipos


def test_prescrever_via_default_e_oral(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["via"] == "Oral"
