from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base

VIAS_PRESCRICAO = ("Oral", "IV", "IM", "SC", "Tópica")


class Prescricao(Base):
    __tablename__ = "prescricoes"

    id = Column(Integer, primary_key=True)
    prontuario_id = Column(Integer, ForeignKey("prontuarios.id"), nullable=False, index=True)
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    medicamento = Column(String, nullable=False)
    dosagem = Column(String, nullable=False)
    via = Column(Enum(*VIAS_PRESCRICAO, name="via_prescricao"), nullable=False)
    frequencia = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    responsavel_matricula = Column(
        String(6), ForeignKey("colaboradores.matricula"), nullable=False
    )

    deleted_at = Column(DateTime(timezone=True), nullable=True)
