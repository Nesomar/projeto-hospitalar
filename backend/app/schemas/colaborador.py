from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import MATRICULA_PATTERN, PIN_PATTERN

PERFIS_CADASTRAVEIS = ("enfermeiro", "medico")


class ColaboradorCreate(BaseModel):
    matricula: str = Field(pattern=MATRICULA_PATTERN)
    pin: str = Field(pattern=PIN_PATTERN)
    nome: str = Field(min_length=1)
    perfil: str = Field(description=f"Um de: {', '.join(PERFIS_CADASTRAVEIS)}")

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nome não pode ser vazio")
        return v

    @field_validator("perfil")
    @classmethod
    def perfil_valido(cls, v: str) -> str:
        if v not in PERFIS_CADASTRAVEIS:
            raise ValueError(f"perfil deve ser um de {PERFIS_CADASTRAVEIS}")
        return v


class ColaboradorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    nome: str
    perfil: str
