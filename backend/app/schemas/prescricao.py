from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.prescricao import VIAS_PRESCRICAO

ViaPrescricao = Literal[*VIAS_PRESCRICAO]


class PrescricaoCreate(BaseModel):
    medicamento: str = Field(min_length=1)
    dosagem: str = Field(min_length=1)
    via: ViaPrescricao = "Oral"
    frequencia: str | None = None
    observacoes: str | None = None


class PrescricaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data: datetime
    medicamento: str
    dosagem: str
    via: str
    frequencia: str | None
    observacoes: str | None
    responsavel_matricula: str
