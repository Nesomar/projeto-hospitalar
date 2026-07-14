from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    cns = Column(String(15), unique=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String, nullable=True)
    telefone = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
