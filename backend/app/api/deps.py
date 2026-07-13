from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.colaborador import Colaborador

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


def get_colaborador_ativo(db: Session, matricula: str) -> Colaborador | None:
    return (
        db.query(Colaborador)
        .filter(Colaborador.matricula == matricula, Colaborador.deleted_at.is_(None))
        .first()
    )


def get_current_colaborador(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: DbDep,
) -> Colaborador:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise credenciais_invalidas

    matricula = payload.get("sub")
    if matricula is None:
        raise credenciais_invalidas

    colaborador = get_colaborador_ativo(db, matricula)
    if colaborador is None:
        raise credenciais_invalidas
    return colaborador


CurrentColaborador = Annotated[Colaborador, Depends(get_current_colaborador)]


def require_perfil(*perfis_permitidos: str) -> Callable[[Colaborador], Colaborador]:
    def checker(colaborador: CurrentColaborador) -> Colaborador:
        if colaborador.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Perfil sem permissão para esta ação",
            )
        return colaborador

    return checker
