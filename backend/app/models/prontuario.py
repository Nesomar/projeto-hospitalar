from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer
from sqlalchemy.sql import func

from app.core.database import Base

CLASSIFICACOES_RISCO = ("vermelho", "laranja", "amarelo", "verde", "azul")


class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    classificacao_risco = Column(
        Enum(*CLASSIFICACOES_RISCO, name="classificacao_risco"), nullable=True
    )
    pas = Column(Integer, nullable=True)
    pad = Column(Integer, nullable=True)
    fc = Column(Integer, nullable=True)
    fr = Column(Integer, nullable=True)
    temp = Column(Float, nullable=True)
    spo2 = Column(Integer, nullable=True)
    dor = Column(Integer, nullable=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True)
