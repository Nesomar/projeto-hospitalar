from pydantic import BaseModel


class SolicitarExamesRequest(BaseModel):
    observacoes: str | None = None


class AtendimentoStatus(BaseModel):
    paciente_id: int
    status: str
