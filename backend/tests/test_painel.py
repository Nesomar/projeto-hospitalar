from app.core.security import create_access_token, hash_pin
from app.models.colaborador import Colaborador


def _cadastrar_paciente(client, auth_headers, cpf, cns, nome="Paciente Teste"):
    resp = client.post(
        "/api/pacientes",
        json={
            "nome": nome,
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


def test_listar_sem_autenticacao_e_recusado(client):
    resp = client.get("/api/painel")
    assert resp.status_code == 403


def test_listar_ordena_por_gravidade_com_nao_classificados_ao_final(client, auth_headers):
    id_verde = _cadastrar_paciente(client, auth_headers, "11111111111", "111111111111111", "Paciente Verde")
    _triar(client, auth_headers, id_verde, dor=2)

    id_vermelho = _cadastrar_paciente(client, auth_headers, "22222222222", "222222222222222", "Paciente Vermelho")
    _triar(client, auth_headers, id_vermelho, spo2=85)

    id_sem_triagem = _cadastrar_paciente(client, auth_headers, "33333333333", "333333333333333", "Paciente Sem Triagem")

    id_laranja = _cadastrar_paciente(client, auth_headers, "44444444444", "444444444444444", "Paciente Laranja")
    _triar(client, auth_headers, id_laranja, fc=130)

    resp = client.get("/api/painel", headers=auth_headers)
    assert resp.status_code == 200
    cores = [item["classificacao_risco"] for item in resp.json()]
    assert cores == ["vermelho", "laranja", "verde", None]


def test_listar_filtra_por_cor(client, auth_headers):
    id_verde = _cadastrar_paciente(client, auth_headers, "11111111111", "111111111111111")
    _triar(client, auth_headers, id_verde, dor=2)

    id_vermelho = _cadastrar_paciente(client, auth_headers, "22222222222", "222222222222222")
    _triar(client, auth_headers, id_vermelho, spo2=85)

    resp = client.get("/api/painel", params={"cor": "verde"}, headers=auth_headers)
    assert resp.status_code == 200
    corpo = resp.json()
    assert len(corpo) == 1
    assert corpo[0]["paciente_id"] == id_verde


def test_listar_cor_invalida_retorna_422(client, auth_headers):
    resp = client.get("/api/painel", params={"cor": "roxo"}, headers=auth_headers)
    assert resp.status_code == 422


def test_pode_fazer_triagem_true_para_enfermeiro_e_aguardando_triagem(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers, "11111111111", "111111111111111")
    headers_enfermeiro = _headers_enfermeiro(db_session)

    resp = client.get("/api/painel", headers=headers_enfermeiro)
    item = next(i for i in resp.json() if i["paciente_id"] == paciente_id)
    assert item["pode_fazer_triagem"] is True


def test_pode_fazer_triagem_false_para_medico(client, auth_headers):
    paciente_id = _cadastrar_paciente(client, auth_headers, "11111111111", "111111111111111")

    resp = client.get("/api/painel", headers=auth_headers)
    item = next(i for i in resp.json() if i["paciente_id"] == paciente_id)
    assert item["pode_fazer_triagem"] is False


def test_pode_fazer_triagem_false_quando_ja_triado(client, auth_headers, db_session):
    paciente_id = _cadastrar_paciente(client, auth_headers, "11111111111", "111111111111111")
    _triar(client, auth_headers, paciente_id, dor=2)
    headers_enfermeiro = _headers_enfermeiro(db_session)

    resp = client.get("/api/painel", headers=headers_enfermeiro)
    item = next(i for i in resp.json() if i["paciente_id"] == paciente_id)
    assert item["pode_fazer_triagem"] is False
