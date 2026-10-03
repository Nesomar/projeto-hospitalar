from datetime import date

from pydantic import BaseModel, ConfigDict, Field

CPF_PATTERN = r"^[0-9]{11}$"
CNS_PATTERN = r"^[0-9]{15}$"


class PacienteCreate(BaseModel):
    nome: str = Field(min_length=3)
    cpf: str = Field(pattern=CPF_PATTERN)
    cns: str = Field(pattern=CNS_PATTERN)
    data_nascimento: date
    sexo: str | None = None
    telefone: str | None = None


class PacienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cpf: str
    cns: str
    data_nascimento: date
    sexo: str | None
    telefone: str | None


class PacienteBusca(PacienteOut):
    atendimento_ativo: bool


class DadosCadastraisRetorno(BaseModel):
    telefone: str | None = None
    sexo: str | None = Field(default=None, pattern=r"^[FMO]$")


class NovoAtendimentoIn(BaseModel):
    dados_cadastrais: DadosCadastraisRetorno | None = None


class NovoAtendimentoOut(BaseModel):
    prontuario_id: int
    paciente_id: int
    status: str
