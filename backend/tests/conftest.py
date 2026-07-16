import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-nao-usar-em-producao")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.database import Base
from app.core.security import create_access_token, hash_pin
from app.main import app
from app.models.colaborador import Colaborador

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _tabelas_limpas():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers(db_session):
    """Simula o bootstrap: cria um colaborador direto no banco (como o
    scripts/seed_colaborador.py faria) e retorna um header Authorization
    valido para um perfil clinico (medico). Usado pela maioria dos testes de
    rotas clinicas (pacientes/painel/prontuario/triagem/atendimento/prescricao).
    Para testar o cadastro de colaborador (POST /api/colaboradores), que exige
    perfil administrador, use a fixture admin_headers."""
    bootstrap = Colaborador(
        matricula="000001", pin_hash=hash_pin("0000"), nome="Bootstrap", perfil="medico"
    )
    db_session.add(bootstrap)
    db_session.commit()
    token = create_access_token(subject=bootstrap.matricula, perfil=bootstrap.perfil)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(db_session):
    """Colaborador com perfil administrador, para testar o cadastro de
    colaborador (POST /api/colaboradores) e a restricao cruzada de AC-9."""
    admin = Colaborador(
        matricula="900000", pin_hash=hash_pin("0000"), nome="Admin Bootstrap", perfil="administrador"
    )
    db_session.add(admin)
    db_session.commit()
    token = create_access_token(subject=admin.matricula, perfil=admin.perfil)
    return {"Authorization": f"Bearer {token}"}
