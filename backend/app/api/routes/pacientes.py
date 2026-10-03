from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.api.deps import ClinicoAtual, DbDep, require_perfil
from app.models.colaborador import Colaborador
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prontuario import Prontuario, status_efetivo
from app.schemas.paciente import (
    CPF_PATTERN,
    DadosCadastraisRetorno,
    NovoAtendimentoIn,
    NovoAtendimentoOut,
    PacienteBusca,
    PacienteCreate,
    PacienteOut,
)

router = APIRouter(prefix="/api", tags=["pacientes"])

_sem_alta = or_(Prontuario.status_atendimento.is_(None), Prontuario.status_atendimento != "alta")


def _tem_atendimento_ativo(db, paciente_id: int) -> bool:
    return (
        db.query(Prontuario.id)
        .filter(Prontuario.paciente_id == paciente_id, Prontuario.deleted_at.is_(None), _sem_alta)
        .first()
        is not None
    )


def _aplicar_dados_cadastrais(paciente: Paciente, dados: DadosCadastraisRetorno | None) -> list[str]:
    """Aplica só o que mudou e devolve os nomes dos campos alterados.
    Campo ausente ou telefone em branco = não alterar (limpar telefone não é suportado)."""
    if dados is None:
        return []
    atualizados = []
    telefone = (dados.telefone or "").strip()
    if telefone and telefone != paciente.telefone:
        paciente.telefone = telefone
        atualizados.append("telefone")
    if dados.sexo and dados.sexo != paciente.sexo:
        paciente.sexo = dados.sexo
        atualizados.append("sexo")
    return atualizados


@router.get("/pacientes", response_model=list[PacienteBusca])
def buscar_paciente_por_cpf(
    db: DbDep,
    colaborador: ClinicoAtual,
    cpf: str = Query(pattern=CPF_PATTERN),
) -> list[PacienteBusca]:
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf, Paciente.deleted_at.is_(None)).first()
    if paciente is None:
        return []
    return [
        PacienteBusca(
            **PacienteOut.model_validate(paciente).model_dump(),
            atendimento_ativo=_tem_atendimento_ativo(db, paciente.id),
        )
    ]


@router.post("/pacientes", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(
    payload: PacienteCreate,
    db: DbDep,
    colaborador: ClinicoAtual,
) -> Paciente:
    paciente = Paciente(
        nome=payload.nome,
        cpf=payload.cpf,
        cns=payload.cns,
        data_nascimento=payload.data_nascimento,
        sexo=payload.sexo,
        telefone=payload.telefone,
    )
    db.add(paciente)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CPF ou CNS já cadastrado")

    prontuario = Prontuario(paciente_id=paciente.id)
    db.add(prontuario)
    db.flush()

    evolucao = Evolucao(
        prontuario_id=prontuario.id,
        tipo="Cadastro",
        descricao="Paciente cadastrado, aguardando triagem.",
        responsavel_matricula=colaborador.matricula,
    )
    db.add(evolucao)
    db.commit()
    db.refresh(paciente)
    return paciente


@router.post(
    "/pacientes/{paciente_id}/atendimentos",
    response_model=NovoAtendimentoOut,
    status_code=status.HTTP_201_CREATED,
)
def abrir_novo_atendimento(
    paciente_id: int,
    db: DbDep,
    colaborador: Annotated[Colaborador, Depends(require_perfil("enfermeiro"))],
    payload: NovoAtendimentoIn | None = None,
) -> NovoAtendimentoOut:
    paciente = (
        db.query(Paciente).filter(Paciente.id == paciente_id, Paciente.deleted_at.is_(None)).first()
    )
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    conflito = HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="Paciente já possui atendimento ativo"
    )
    if _tem_atendimento_ativo(db, paciente_id):
        raise conflito

    prontuario = Prontuario(paciente_id=paciente_id)
    db.add(prontuario)
    try:
        db.flush()  # índice único parcial fecha a corrida entre aberturas concorrentes
    except IntegrityError:
        db.rollback()
        raise conflito

    descricao = "Retorno do paciente, aguardando triagem."
    atualizados = _aplicar_dados_cadastrais(paciente, payload.dados_cadastrais if payload else None)
    if atualizados:
        descricao += f" Dados atualizados: {', '.join(atualizados)}."

    db.add(
        Evolucao(
            prontuario_id=prontuario.id,
            tipo="Cadastro",
            descricao=descricao,
            responsavel_matricula=colaborador.matricula,
        )
    )
    db.commit()
    return NovoAtendimentoOut(
        prontuario_id=prontuario.id, paciente_id=paciente_id, status=status_efetivo(prontuario)
    )
