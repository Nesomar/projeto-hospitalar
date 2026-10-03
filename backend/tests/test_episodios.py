from app.core.security import create_access_token, hash_pin
from app.models.colaborador import Colaborador
from app.models.evolucao import Evolucao
from app.models.prescricao import Prescricao
from app.models.prontuario import Prontuario

CPF = "12345678901"


def _cadastrar(client, headers, cpf=CPF, cns="123456789012345"):
    resp = client.post(
        "/api/pacientes",
        json={"nome": "Maria Aparecida Souza", "cpf": cpf, "cns": cns, "data_nascimento": "1958-05-12"},
        headers=headers,
    )
    return resp.json()["id"]


def _enfermeiro(db_session):
    e = Colaborador(
        matricula="654321", pin_hash=hash_pin("0000"), nome="Enfermeira Ana", perfil="enfermeiro"
    )
    db_session.add(e)
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token(subject=e.matricula, perfil=e.perfil)}"}


def _dar_alta(client, medico, paciente_id):
    client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar",
        json={"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0},
        headers=medico,
    )
    client.post(f"/api/pacientes/{paciente_id}/atendimento/iniciar", headers=medico)
    resp = client.post(f"/api/pacientes/{paciente_id}/atendimento/alta", headers=medico)
    assert resp.status_code == 200


def _novo_atendimento(client, headers, paciente_id):
    return client.post(f"/api/pacientes/{paciente_id}/atendimentos", headers=headers)


def test_retorno_apos_alta_cria_novo_prontuario_e_aparece_no_painel(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _cadastrar(client, auth_headers)
    _dar_alta(client, auth_headers, pid)

    resp = _novo_atendimento(client, enf, pid)
    assert resp.status_code == 201
    assert resp.json()["status"] == "Aguardando Triagem"

    assert db_session.query(Prontuario).filter_by(paciente_id=pid).count() == 2
    evolucao = (
        db_session.query(Evolucao)
        .filter_by(descricao="Retorno do paciente, aguardando triagem.")
        .one()
    )
    assert evolucao.responsavel_matricula == "654321"
    painel = client.get("/api/painel", headers=auth_headers).json()
    assert any(i["paciente_id"] == pid for i in painel)


def test_retorno_com_atendimento_ativo_retorna_409(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _cadastrar(client, auth_headers)

    resp = _novo_atendimento(client, enf, pid)
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Paciente já possui atendimento ativo"


def test_retorno_paciente_inexistente_retorna_404(client, db_session):
    assert _novo_atendimento(client, _enfermeiro(db_session), 999).status_code == 404


def test_medico_nao_abre_atendimento(client, auth_headers):
    pid = _cadastrar(client, auth_headers)
    assert _novo_atendimento(client, auth_headers, pid).status_code == 403


def test_busca_por_cpf(client, auth_headers):
    pid = _cadastrar(client, auth_headers)

    achado = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()
    assert [(p["id"], p["atendimento_ativo"]) for p in achado] == [(pid, True)]

    _dar_alta(client, auth_headers, pid)
    achado = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()
    assert achado[0]["atendimento_ativo"] is False

    assert client.get("/api/pacientes?cpf=99999999999", headers=auth_headers).json() == []


def test_prescricao_com_dois_episodios_cai_no_ativo(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _cadastrar(client, auth_headers)
    _dar_alta(client, auth_headers, pid)
    _novo_atendimento(client, enf, pid)

    resp = client.post(
        f"/api/pacientes/{pid}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    ativo = db_session.query(Prontuario).filter_by(paciente_id=pid, status_atendimento=None).one()
    assert db_session.query(Prescricao).one().prontuario_id == ativo.id


def test_prescricao_sem_atendimento_ativo_retorna_409(client, auth_headers):
    pid = _cadastrar(client, auth_headers)
    _dar_alta(client, auth_headers, pid)

    resp = client.post(
        f"/api/pacientes/{pid}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Paciente não possui atendimento ativo"


def test_historico_com_duas_visitas_encerradas(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _cadastrar(client, auth_headers)
    _dar_alta(client, auth_headers, pid)
    _novo_atendimento(client, enf, pid)
    _dar_alta(client, auth_headers, pid)
    _novo_atendimento(client, enf, pid)  # terceiro, ativo: fora do histórico

    resp = client.get(f"/api/pacientes/{pid}/atendimentos", headers=auth_headers)
    assert resp.status_code == 200
    itens = resp.json()
    assert len(itens) == 2
    assert itens[0]["prontuario_id"] > itens[1]["prontuario_id"]
    for item in itens:
        assert item["data_alta"] is not None
        assert item["sinais_vitais"]["pas"] == 100
        assert {e["tipo"] for e in item["evolucoes"]} >= {"Cadastro", "Alta"}
    ativo = db_session.query(Prontuario).filter_by(paciente_id=pid, status_atendimento=None).one()
    assert ativo.id not in [i["prontuario_id"] for i in itens]


def test_historico_primeira_visita_e_vazio(client, auth_headers):
    pid = _cadastrar(client, auth_headers)
    resp = client.get(f"/api/pacientes/{pid}/atendimentos", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_historico_paciente_inexistente_retorna_404(client, auth_headers):
    assert client.get("/api/pacientes/999/atendimentos", headers=auth_headers).status_code == 404


# --- atualização de dados cadastrais no retorno ---


def _paciente_com_alta(client, auth_headers, telefone="(81) 99999-0000", sexo="F"):
    resp = client.post(
        "/api/pacientes",
        json={
            "nome": "Maria Aparecida Souza",
            "cpf": CPF,
            "cns": "123456789012345",
            "data_nascimento": "1958-05-12",
            "sexo": sexo,
            "telefone": telefone,
        },
        headers=auth_headers,
    )
    pid = resp.json()["id"]
    _dar_alta(client, auth_headers, pid)
    return pid


def _retorno(client, enf, pid, dados=None):
    body = None if dados is None else {"dados_cadastrais": dados}
    return client.post(f"/api/pacientes/{pid}/atendimentos", json=body, headers=enf)


def _descricao_retorno(db_session):
    return db_session.query(Evolucao).filter(Evolucao.descricao.like("Retorno do paciente%")).one().descricao


def test_retorno_atualiza_telefone_e_registra_na_evolucao(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _paciente_com_alta(client, auth_headers)

    resp = _retorno(client, enf, pid, {"telefone": "(81) 98888-1111", "sexo": "F"})
    assert resp.status_code == 201

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] == "(81) 98888-1111"
    assert paciente["sexo"] == "F"
    assert _descricao_retorno(db_session) == "Retorno do paciente, aguardando triagem. Dados atualizados: telefone."


def test_retorno_atualiza_telefone_e_sexo(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _paciente_com_alta(client, auth_headers)

    _retorno(client, enf, pid, {"telefone": "(81) 98888-1111", "sexo": "O"})

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert (paciente["telefone"], paciente["sexo"]) == ("(81) 98888-1111", "O")
    assert _descricao_retorno(db_session).endswith("Dados atualizados: telefone, sexo.")


def test_retorno_sem_dados_ou_valores_iguais_nao_altera(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _paciente_com_alta(client, auth_headers)

    assert _retorno(client, enf, pid, {"telefone": "(81) 99999-0000", "sexo": "F"}).status_code == 201

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] == "(81) 99999-0000"
    assert _descricao_retorno(db_session) == "Retorno do paciente, aguardando triagem."


def test_retorno_telefone_em_branco_nao_apaga_telefone(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _paciente_com_alta(client, auth_headers)

    _retorno(client, enf, pid, {"telefone": "  "})

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] == "(81) 99999-0000"


def test_retorno_sexo_invalido_retorna_422_sem_efeitos(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _paciente_com_alta(client, auth_headers)

    resp = _retorno(client, enf, pid, {"telefone": "(81) 98888-1111", "sexo": "X"})
    assert resp.status_code == 422

    assert db_session.query(Prontuario).filter_by(paciente_id=pid).count() == 1
    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] == "(81) 99999-0000"


def test_retorno_com_atendimento_ativo_nao_altera_paciente(client, auth_headers, db_session):
    enf = _enfermeiro(db_session)
    pid = _cadastrar(client, auth_headers)

    resp = _retorno(client, enf, pid, {"telefone": "(81) 98888-1111"})
    assert resp.status_code == 409

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] is None


def test_medico_nao_atualiza_dados_no_retorno(client, auth_headers):
    pid = _paciente_com_alta(client, auth_headers)

    assert _retorno(client, auth_headers, pid, {"telefone": "(81) 98888-1111"}).status_code == 403

    paciente = client.get(f"/api/pacientes?cpf={CPF}", headers=auth_headers).json()[0]
    assert paciente["telefone"] == "(81) 99999-0000"
