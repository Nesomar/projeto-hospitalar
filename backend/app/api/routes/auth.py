from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentColaborador, DbDep, get_colaborador_ativo
from app.core.security import create_access_token, hash_pin, verify_pin
from app.models.colaborador import Colaborador
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.colaborador import ColaboradorCreate, ColaboradorOut

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/colaboradores", response_model=ColaboradorOut, status_code=status.HTTP_201_CREATED)
def cadastrar_colaborador(
    payload: ColaboradorCreate,
    db: DbDep,
    _autenticado: CurrentColaborador,
) -> Colaborador:
    existente = db.query(Colaborador).filter(Colaborador.matricula == payload.matricula).first()
    if existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    colaborador = Colaborador(
        matricula=payload.matricula,
        pin_hash=hash_pin(payload.pin),
        nome=payload.nome,
        perfil=payload.perfil,
    )
    db.add(colaborador)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")
    db.refresh(colaborador)
    return colaborador


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbDep) -> TokenResponse:
    colaborador = get_colaborador_ativo(db, payload.matricula)
    pin_hash = colaborador.pin_hash if colaborador is not None else None
    if colaborador is None or not verify_pin(payload.pin, pin_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    access_token = create_access_token(subject=colaborador.matricula, perfil=colaborador.perfil)
    return TokenResponse(access_token=access_token)
