from pydantic import BaseModel


class PainelItem(BaseModel):
    paciente_id: int
    nome: str
    classificacao_risco: str | None
    status: str
    pode_fazer_triagem: bool
