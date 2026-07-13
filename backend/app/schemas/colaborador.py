from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.colaborador import PERFIS_COLABORADOR
from app.schemas.auth import MATRICULA_PATTERN, PIN_PATTERN


class ColaboradorCreate(BaseModel):
    matricula: str = Field(pattern=MATRICULA_PATTERN)
    pin: str = Field(pattern=PIN_PATTERN)
    nome: str
    perfil: str = Field(description=f"Um de: {', '.join(PERFIS_COLABORADOR)}")

    @field_validator("perfil")
    @classmethod
    def perfil_valido(cls, v: str) -> str:
        if v not in PERFIS_COLABORADOR:
            raise ValueError(f"perfil deve ser um de {PERFIS_COLABORADOR}")
        return v


class ColaboradorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricula: str
    nome: str
    perfil: str
