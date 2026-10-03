from datetime import date, datetime

from pydantic import BaseModel


class SinaisVitaisAtuais(BaseModel):
    classificacao_risco: str | None
    pas: int | None
    pad: int | None
    fc: int | None
    fr: int | None
    temp: float | None
    spo2: int | None
    dor: int | None


class EvolucaoItem(BaseModel):
    id: int
    data: datetime
    tipo: str
    descricao: str
    responsavel_matricula: str

    class Config:
        from_attributes = True


class PrescricaoItem(BaseModel):
    id: int
    data: datetime
    medicamento: str
    dosagem: str
    via: str
    frequencia: str | None
    observacoes: str | None
    responsavel_matricula: str

    class Config:
        from_attributes = True


class PacienteResumo(BaseModel):
    data_nascimento: date
    sexo: str | None
    cpf: str
    cns: str
    telefone: str | None


class ProntuarioResponse(BaseModel):
    paciente_id: int
    paciente_nome: str
    paciente: PacienteResumo
    queixa: str | None
    status: str
    sinais_vitais: SinaisVitaisAtuais
    evolucoes: list[EvolucaoItem]
    prescricoes: list[PrescricaoItem]
    pode_prescrever: bool
    pode_iniciar_atendimento: bool
    pode_dar_alta: bool
    pode_solicitar_exames: bool
    pode_retomar_atendimento: bool
