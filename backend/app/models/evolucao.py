from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Evolucao(Base):
    __tablename__ = "evolucoes"

    id = Column(Integer, primary_key=True)
    prontuario_id = Column(Integer, ForeignKey("prontuarios.id"), nullable=False, index=True)
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tipo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    responsavel_matricula = Column(
        String(6), ForeignKey("colaboradores.matricula"), nullable=False
    )

    deleted_at = Column(DateTime(timezone=True), nullable=True)
