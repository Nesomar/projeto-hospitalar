from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index, Integer, Text, text
from sqlalchemy.sql import func

from app.core.database import Base

CLASSIFICACOES_RISCO = ("vermelho", "laranja", "amarelo", "verde", "azul")
STATUS_ATENDIMENTO = ("em_atendimento", "aguardando_exames", "alta")

# Atendimento ativo = nao deletado e sem alta. Mesmo predicado na migracao 0006.
_ATIVO = "deleted_at IS NULL AND (status_atendimento IS NULL OR status_atendimento <> 'alta')"


class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    classificacao_risco = Column(
        Enum(*CLASSIFICACOES_RISCO, name="classificacao_risco"), nullable=True
    )
    status_atendimento = Column(
        Enum(*STATUS_ATENDIMENTO, name="status_atendimento"), nullable=True
    )
    pas = Column(Integer, nullable=True)
    pad = Column(Integer, nullable=True)
    fc = Column(Integer, nullable=True)
    fr = Column(Integer, nullable=True)
    temp = Column(Float, nullable=True)
    spo2 = Column(Integer, nullable=True)
    dor = Column(Integer, nullable=True)
    queixa = Column(Text, nullable=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "uq_prontuario_ativo_por_paciente",
            "paciente_id",
            unique=True,
            postgresql_where=text(_ATIVO),
            sqlite_where=text(_ATIVO),
        ),
    )


_STATUS_LABELS = {
    "em_atendimento": "Em Atendimento",
    "aguardando_exames": "Aguardando Exames Complementares",
    "alta": "Alta",
}


def status_efetivo(prontuario: "Prontuario") -> str:
    if prontuario.status_atendimento:
        return _STATUS_LABELS[prontuario.status_atendimento]
    if prontuario.classificacao_risco:
        return "Aguardando Atendimento"
    return "Aguardando Triagem"


def acoes_medicas(perfil: str, status: str) -> dict[str, bool]:
    e_medico = perfil == "medico"
    return {
        "pode_iniciar_atendimento": e_medico and status == "Aguardando Atendimento",
        "pode_dar_alta": e_medico and status == "Em Atendimento",
        "pode_solicitar_exames": e_medico and status == "Em Atendimento",
        "pode_retomar_atendimento": e_medico and status == "Aguardando Exames Complementares",
    }
