from pydantic import BaseModel


class PainelItem(BaseModel):
    paciente_id: int
    nome: str
    classificacao_risco: str | None
    status: str
    pode_fazer_triagem: bool
    pode_iniciar_atendimento: bool
    pode_dar_alta: bool
    pode_solicitar_exames: bool
    pode_retomar_atendimento: bool
