from pydantic import BaseModel, Field


class SinaisVitais(BaseModel):
    pas: int = Field(ge=0)
    fc: int = Field(ge=0)
    temp: float = Field(ge=0)
    spo2: int = Field(ge=0, le=100)
    pad: int | None = Field(default=None, ge=0)
    fr: int | None = Field(default=None, ge=0)
    dor: int = Field(default=0, ge=0, le=10)


class TriagemResultado(BaseModel):
    cor: str
    tempo_meta: str
    justificativa: str


class ConfirmarTriagemRequest(SinaisVitais):
    queixa: str | None = None
