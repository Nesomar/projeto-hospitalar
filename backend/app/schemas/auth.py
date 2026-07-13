from pydantic import BaseModel, Field

MATRICULA_PATTERN = r"^[0-9]{6}$"
PIN_PATTERN = r"^[0-9]{4}$"


class LoginRequest(BaseModel):
    matricula: str = Field(pattern=MATRICULA_PATTERN)
    pin: str = Field(pattern=PIN_PATTERN)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
