from app.core.security import create_access_token, hash_pin
from app.models.colaborador import Colaborador
from app.models.prescricao import Prescricao
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


def test_consultar_sem_autenticacao_e_recusado(client):
    resp = client.get("/api/pacientes/1/prontuario")
    assert resp.status_code == 403


def test_consultar_paciente_inexistente_retorna_404(client, auth_headers):
    resp = client.get("/api/pacientes/99999/prontuario", headers=auth_headers)
    assert resp.status_code == 404


def test_consultar_exibe_sinais_evolucoes_e_prescricoes(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar",
        json={"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 2, "queixa": "Dor de cabeça"},
        headers=auth_headers,
    )

    prontuario = db_session.query(Prontuario).filter_by(paciente_id=paciente_id).one()
    prescricao = Prescricao(
        prontuario_id=prontuario.id,
        medicamento="Dipirona",
        dosagem="500mg",
        via="Oral",
        frequencia="8/8h",
        responsavel_matricula="000001",
    )
    db_session.add(prescricao)
    db_session.commit()

    resp = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=auth_headers)
    assert resp.status_code == 200
    corpo = resp.json()

    assert corpo["sinais_vitais"]["classificacao_risco"] == "verde"
    tipos_evolucao = [e["tipo"] for e in corpo["evolucoes"]]
    assert tipos_evolucao == ["Triagem", "Cadastro"]
    assert corpo["prescricoes"][0]["medicamento"] == "Dipirona"


def test_consultar_sem_prescricoes_retorna_lista_vazia(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar",
        json={"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 2},
        headers=auth_headers,
    )

    resp = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["prescricoes"] == []


def test_pode_prescrever_true_para_medico(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    resp = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=auth_headers)
    assert resp.json()["pode_prescrever"] is True


def test_pode_prescrever_false_para_enfermeiro(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    headers_enfermeiro = _headers_enfermeiro(db_session)

    resp = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=headers_enfermeiro)
    assert resp.json()["pode_prescrever"] is False


def _triar_e_iniciar(client, auth_headers, paciente_id, queixa=None):
    vitais = {"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0}
    if queixa:
        vitais["queixa"] = queixa
    client.post(f"/api/pacientes/{paciente_id}/triagem/confirmar", json=vitais, headers=auth_headers)
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=auth_headers)


def test_medico_em_atendimento_recebe_dados_paciente_e_flags(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar_e_iniciar(client, auth_headers, paciente_id, queixa="Dor no peito")

    dados = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=auth_headers).json()

    assert dados["paciente"] == {
        "data_nascimento": "1958-05-12",
        "sexo": None,
        "cpf": "12345678901",
        "cns": "123456789012345",
        "telefone": None,
    }
    assert dados["queixa"] == "Dor no peito"
    assert dados["status"] == "Em Atendimento"
    assert dados["pode_dar_alta"] is True
    assert dados["pode_solicitar_exames"] is True
    assert dados["pode_iniciar_atendimento"] is False
    assert dados["pode_retomar_atendimento"] is False


def test_enfermeiro_recebe_todas_flags_medicas_falsas(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers)
    _triar_e_iniciar(client, auth_headers, paciente_id)

    dados = client.get(
        f"/api/pacientes/{paciente_id}/prontuario", headers=_headers_enfermeiro(db_session)
    ).json()

    assert dados["status"] == "Em Atendimento"
    assert dados["paciente"]["cpf"] == "12345678901"
    for flag in ("pode_iniciar_atendimento", "pode_dar_alta", "pode_solicitar_exames", "pode_retomar_atendimento"):
        assert dados[flag] is False


def test_prontuario_sem_queixa_retorna_nulo(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers)

    dados = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=auth_headers).json()

    assert dados["queixa"] is None
    assert dados["status"] == "Aguardando Triagem"
