from datetime import datetime, timedelta, timezone
from functools import lru_cache

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

JWT_ALGORITHM = "HS256"


@lru_cache(maxsize=1)
def _dummy_pin_hash() -> str:
    # Hash bcrypt válido de um PIN nunca cadastrado — usado para consumir o mesmo
    # tempo de verificação de uma matrícula existente quando ela não é encontrada,
    # evitando que o tempo de resposta revele se a matrícula existe (user enumeration).
    return bcrypt.hashpw(b"0000", bcrypt.gensalt()).decode("utf-8")


def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_pin(pin: str, pin_hash: str | None) -> bool:
    target = pin_hash or _dummy_pin_hash()
    return bcrypt.checkpw(pin.encode("utf-8"), target.encode("utf-8"))


def create_access_token(subject: str, perfil: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "perfil": perfil, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Token inválido ou expirado") from exc
