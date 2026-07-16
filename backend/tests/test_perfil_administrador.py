"""Testes da feature perfil-administrador (docs/specs/perfil-administrador.md).

Cobre RBAC do cadastro de colaborador (POST /api/colaboradores restrito a
administrador) e a restricao cruzada de AC-9 (administrador nao acessa rotas
clinicas). O happy-path completo de cadastro (201, hash de PIN, 409 de
matricula duplicada/corrida, 422 de formato) ja e coberto por test_auth.py
usando a fixture admin_headers; este arquivo foca nos criterios de aceite que
ainda nao tinham cobertura antes desta feature.
"""

from datetime import datetime, timezone

import pytest

from app.core.security import create_access_token, hash_pin
from app.models.colaborador import Colaborador


def _cadastrar(client, headers, matricula="123456", pin="1234", nome="Colaborador Teste", perfil="enfermeiro"):
    return client.post(
        "/api/colaboradores",
        json={"matricula": matricula, "pin": pin, "nome": nome, "perfil": perfil},
        headers=headers,
    )


def _headers_perfil(db_session, perfil, matricula="654321"):
    colaborador = Colaborador(
        matricula=matricula, pin_hash=hash_pin("0000"), nome="Colaborador Existente", perfil=perfil
    )
    db_session.add(colaborador)
    db_session.commit()
    token = create_access_token(subject=colaborador.matricula, perfil=colaborador.perfil)
    return {"Authorization": f"Bearer {token}"}


# --- AC-1 / AC-2: administrador cadastra, colaborador criado consegue logar ---


def test_ac1_ac2_administrador_cadastra_e_colaborador_consegue_logar(client, admin_headers):
    resp = _cadastrar(client, admin_headers, matricula="111222", pin="4321", perfil="medico")
    assert resp.status_code == 201
    body = resp.json()
    assert body["matricula"] == "111222"
    assert body["perfil"] == "medico"

    login = client.post("/api/auth/login", json={"matricula": "111222", "pin": "4321"})
    assert login.status_code == 200
    assert login.json()["access_token"]


# --- AC-1 / AC-10: enfermeiro e medico recebem 403 ao tentar cadastrar colaborador ---


def test_ac1_ac10_enfermeiro_recebe_403_ao_cadastrar_colaborador(client, db_session):
    headers = _headers_perfil(db_session, "enfermeiro")
    resp = _cadastrar(client, headers)
    assert resp.status_code == 403


def test_ac1_ac10_medico_recebe_403_ao_cadastrar_colaborador(client, db_session):
    headers = _headers_perfil(db_session, "medico")
    resp = _cadastrar(client, headers)
    assert resp.status_code == 403


# --- AC-3: perfil "administrador" nao e opcao valida no cadastro de colaborador ---


def test_ac3_cadastro_com_perfil_administrador_e_rejeitado_422(client, admin_headers):
    resp = _cadastrar(client, admin_headers, perfil="administrador")
    assert resp.status_code == 422


# --- AC-4: matricula duplicada, inclusive de colaborador soft-deletado ---


def test_ac4_matricula_de_colaborador_soft_deletado_e_rejeitada_409(client, admin_headers, db_session):
    inativo = Colaborador(
        matricula="777888",
        pin_hash=hash_pin("0000"),
        nome="Ex Colaborador",
        perfil="enfermeiro",
        deleted_at=datetime.now(timezone.utc),
    )
    db_session.add(inativo)
    db_session.commit()

    resp = _cadastrar(client, admin_headers, matricula="777888")
    assert resp.status_code == 409
    # nao duplica nem reativa o registro existente
    registros = db_session.query(Colaborador).filter_by(matricula="777888").all()
    assert len(registros) == 1
    assert registros[0].deleted_at is not None


# --- AC-5 / casos de borda: nome vazio ou so com espacos ---


def test_ac5_nome_vazio_e_rejeitado_422(client, admin_headers):
    resp = _cadastrar(client, admin_headers, nome="")
    assert resp.status_code == 422


def test_ac5_nome_apenas_espacos_e_rejeitado_422(client, admin_headers):
    resp = _cadastrar(client, admin_headers, nome="   ")
    assert resp.status_code == 422


# --- AC-6: nao autenticado / token invalido ou expirado na rota de cadastro ---


def test_ac6_cadastro_com_token_invalido_retorna_401(client):
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "999888", "pin": "1234", "nome": "Teste", "perfil": "enfermeiro"},
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert resp.status_code == 401


def test_ac6_cadastro_sem_token_retorna_403(client):
    # HTTPBearer recusa a requisicao com 403 antes mesmo de chegar em
    # get_current_colaborador quando o header Authorization esta ausente
    # (comportamento padrao do FastAPI para essa security scheme) - mesma
    # convencao ja usada nos demais testes "sem_autenticacao" do projeto.
    resp = client.post(
        "/api/colaboradores",
        json={"matricula": "999888", "pin": "1234", "nome": "Teste", "perfil": "enfermeiro"},
    )
    assert resp.status_code == 403


# --- AC-9: administrador nao acessa nenhuma acao clinica ---


def test_ac9_administrador_recebe_403_ao_cadastrar_paciente(client, admin_headers):
    resp = client.post(
        "/api/pacientes",
        json={
            "nome": "Paciente Teste",
            "cpf": "12345678901",
            "cns": "123456789012345",
            "data_nascimento": "1958-05-12",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 403


def test_ac9_administrador_recebe_403_ao_consultar_painel(client, admin_headers):
    resp = client.get("/api/painel", headers=admin_headers)
    assert resp.status_code == 403


def test_ac9_administrador_recebe_403_ao_calcular_triagem(client, admin_headers):
    resp = client.post(
        "/api/triagem/calcular",
        json={"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0},
        headers=admin_headers,
    )
    assert resp.status_code == 403


def test_ac9_administrador_recebe_403_ao_confirmar_triagem(client, admin_headers, auth_headers):
    # paciente precisa existir; cadastro feito por um clinico (medico) valido
    paciente = client.post(
        "/api/pacientes",
        json={
            "nome": "Paciente Teste",
            "cpf": "98765432100",
            "cns": "987654321000000",
            "data_nascimento": "1958-05-12",
        },
        headers=auth_headers,
    )
    paciente_id = paciente.json()["id"]

    resp = client.post(
        f"/api/pacientes/{paciente_id}/triagem/confirmar",
        json={"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0},
        headers=admin_headers,
    )
    assert resp.status_code == 403


def test_ac9_administrador_recebe_403_ao_consultar_prontuario(client, admin_headers, auth_headers):
    paciente = client.post(
        "/api/pacientes",
        json={
            "nome": "Paciente Teste",
            "cpf": "11122233344",
            "cns": "111222333444555",
            "data_nascimento": "1958-05-12",
        },
        headers=auth_headers,
    )
    paciente_id = paciente.json()["id"]

    resp = client.get(f"/api/pacientes/{paciente_id}/prontuario", headers=admin_headers)
    assert resp.status_code == 403


def test_ac9_administrador_recebe_403_ao_prescrever(client, admin_headers, auth_headers):
    paciente = client.post(
        "/api/pacientes",
        json={
            "nome": "Paciente Teste",
            "cpf": "55566677788",
            "cns": "555666777888999",
            "data_nascimento": "1958-05-12",
        },
        headers=auth_headers,
    )
    paciente_id = paciente.json()["id"]

    resp = client.post(
        f"/api/pacientes/{paciente_id}/prescricoes",
        json={"medicamento": "Dipirona", "dosagem": "500mg"},
        headers=admin_headers,
    )
    assert resp.status_code == 403
