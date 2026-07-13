from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base

PERFIS_COLABORADOR = ("enfermeiro", "medico")


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(6), unique=True, nullable=False, index=True)
    pin_hash = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    perfil = Column(Enum(*PERFIS_COLABORADOR, name="perfil_colaborador"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
