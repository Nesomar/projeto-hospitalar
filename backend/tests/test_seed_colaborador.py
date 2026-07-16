"""Testes do script de bootstrap backend/scripts/seed_colaborador.py
(AC-7, AC-8 e casos de borda de docs/specs/perfil-administrador.md).

O script cria o colaborador via app.core.database.SessionLocal (banco real,
fora da API). Para poder validar login via TestClient depois do bootstrap
(AC-7) sem depender de um banco fisico, redirecionamos SessionLocal para o
mesmo engine sqlite in-memory compartilhado com o resto da suite
(tests/conftest.py), que ja tem as tabelas criadas pela fixture autouse
_tabelas_limpas.
"""

import sys

import pytest

import scripts.seed_colaborador as seed_colaborador
from app.core.security import decode_access_token
from app.models.colaborador import Colaborador
from tests.conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def _sessionlocal_de_teste(monkeypatch):
    monkeypatch.setattr(seed_colaborador, "SessionLocal", TestingSessionLocal)


def _run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["seed_colaborador.py", *args])
    seed_colaborador.main()


# --- AC-7: script cria administrador funcional (login imediato) ---


def test_ac7_bootstrap_cria_administrador_que_consegue_logar(client, monkeypatch):
    _run(
        monkeypatch,
        "--matricula", "900001",
        "--pin", "1357",
        "--nome", "Admin Bootstrap",
        "--perfil", "administrador",
    )

    resp = client.post("/api/auth/login", json={"matricula": "900001", "pin": "1357"})
    assert resp.status_code == 200

    payload = decode_access_token(resp.json()["access_token"])
    assert payload["sub"] == "900001"
    assert payload["perfil"] == "administrador"


# --- AC-8: script falha com matricula ja cadastrada, sem duplicar/alterar ---


def test_ac8_bootstrap_falha_com_matricula_ja_cadastrada(client, monkeypatch, db_session, capsys):
    _run(
        monkeypatch,
        "--matricula", "900002",
        "--pin", "1111",
        "--nome", "Admin Original",
        "--perfil", "administrador",
    )

    with pytest.raises(SystemExit) as exc_info:
        _run(
            monkeypatch,
            "--matricula", "900002",
            "--pin", "2222",
            "--nome", "Admin Sobrescrito",
            "--perfil", "administrador",
        )
    assert exc_info.value.code == 2
    assert "ja cadastrada" in capsys.readouterr().err

    registros = db_session.query(Colaborador).filter_by(matricula="900002").all()
    assert len(registros) == 1
    assert registros[0].nome == "Admin Original"


def test_ac8_bootstrap_falha_se_matricula_pertence_a_qualquer_outro_perfil(client, monkeypatch, db_session):
    # AC-8 exige checar "qualquer colaborador, de qualquer perfil" - nao so administrador
    _run(
        monkeypatch,
        "--matricula", "900003",
        "--pin", "1111",
        "--nome", "Enfermeira Existente",
        "--perfil", "enfermeiro",
    )

    with pytest.raises(SystemExit) as exc_info:
        _run(
            monkeypatch,
            "--matricula", "900003",
            "--pin", "2222",
            "--nome", "Admin Novo",
            "--perfil", "administrador",
        )
    assert exc_info.value.code == 2

    registros = db_session.query(Colaborador).filter_by(matricula="900003").all()
    assert len(registros) == 1
    assert registros[0].perfil == "enfermeiro"


# --- Caso de borda: execucao repetida do script (idempotencia sem duplicar) ---


def test_bootstrap_execucao_repetida_nao_duplica(client, monkeypatch, db_session):
    args = (
        "--matricula", "900004",
        "--pin", "4444",
        "--nome", "Admin Repetido",
        "--perfil", "administrador",
    )
    _run(monkeypatch, *args)
    with pytest.raises(SystemExit):
        _run(monkeypatch, *args)
    with pytest.raises(SystemExit):
        _run(monkeypatch, *args)

    assert db_session.query(Colaborador).filter_by(matricula="900004").count() == 1


# --- Casos de borda: matricula/PIN fora do padrao falham antes de persistir ---


def test_bootstrap_matricula_formato_invalido_falha_antes_de_persistir(monkeypatch, db_session, capsys):
    with pytest.raises(SystemExit) as exc_info:
        _run(
            monkeypatch,
            "--matricula", "12345",
            "--pin", "1234",
            "--nome", "Invalido",
            "--perfil", "administrador",
        )
    assert exc_info.value.code == 2
    assert "matricula" in capsys.readouterr().err
    assert db_session.query(Colaborador).count() == 0


def test_bootstrap_pin_formato_invalido_falha_antes_de_persistir(monkeypatch, db_session, capsys):
    with pytest.raises(SystemExit) as exc_info:
        _run(
            monkeypatch,
            "--matricula", "900005",
            "--pin", "12a4",
            "--nome", "Invalido",
            "--perfil", "administrador",
        )
    assert exc_info.value.code == 2
    assert "pin" in capsys.readouterr().err
    assert db_session.query(Colaborador).count() == 0
