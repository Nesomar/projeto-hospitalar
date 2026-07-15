from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbDep, require_perfil
from app.models.colaborador import Colaborador
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prontuario import Prontuario, status_efetivo
from app.schemas.atendimento import AtendimentoStatus, SolicitarExamesRequest

router = APIRouter(prefix="/api", tags=["atendimento"])

MedicoAtual = Annotated[Colaborador, Depends(require_perfil("medico"))]


def _get_prontuario(paciente_id: int, db: DbDep) -> Prontuario:
    paciente = (
        db.query(Paciente).filter(Paciente.id == paciente_id, Paciente.deleted_at.is_(None)).first()
    )
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    prontuario = (
        db.query(Prontuario)
        .filter(Prontuario.paciente_id == paciente_id, Prontuario.deleted_at.is_(None))
        .first()
    )
    if prontuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prontuário não encontrado")
    return prontuario


def _transicionar(
    prontuario: Prontuario,
    db: DbDep,
    colaborador: Colaborador,
    *,
    de: str | None,
    para: str | None,
    tipo_evolucao: str,
    descricao: str,
) -> AtendimentoStatus:
    if prontuario.status_atendimento != de:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Paciente não está em condição para esta transição (status atual: {status_efetivo(prontuario)})",
        )

    prontuario.status_atendimento = para
    evolucao = Evolucao(
        prontuario_id=prontuario.id,
        tipo=tipo_evolucao,
        descricao=descricao,
        responsavel_matricula=colaborador.matricula,
    )
    db.add(evolucao)
    db.commit()

    return AtendimentoStatus(paciente_id=prontuario.paciente_id, status=status_efetivo(prontuario))


@router.post("/pacientes/{paciente_id}/atendimento/iniciar", response_model=AtendimentoStatus)
def iniciar_atendimento(
    paciente_id: int, db: DbDep, colaborador: MedicoAtual
) -> AtendimentoStatus:
    prontuario = _get_prontuario(paciente_id, db)
    if prontuario.classificacao_risco is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Paciente ainda não foi triado"
        )
    return _transicionar(
        prontuario,
        db,
        colaborador,
        de=None,
        para="em_atendimento",
        tipo_evolucao="Início de Atendimento",
        descricao="Atendimento médico iniciado.",
    )


@router.post("/pacientes/{paciente_id}/atendimento/alta", response_model=AtendimentoStatus)
def dar_alta(paciente_id: int, db: DbDep, colaborador: MedicoAtual) -> AtendimentoStatus:
    prontuario = _get_prontuario(paciente_id, db)
    return _transicionar(
        prontuario,
        db,
        colaborador,
        de="em_atendimento",
        para="alta",
        tipo_evolucao="Alta",
        descricao="Paciente recebeu alta.",
    )


@router.post("/pacientes/{paciente_id}/atendimento/exames", response_model=AtendimentoStatus)
def solicitar_exames(
    paciente_id: int, payload: SolicitarExamesRequest, db: DbDep, colaborador: MedicoAtual
) -> AtendimentoStatus:
    prontuario = _get_prontuario(paciente_id, db)
    observacoes = payload.observacoes or "sem observações"
    return _transicionar(
        prontuario,
        db,
        colaborador,
        de="em_atendimento",
        para="aguardando_exames",
        tipo_evolucao="Solicitação de Exames",
        descricao=f"Exames complementares solicitados — {observacoes}.",
    )


@router.post("/pacientes/{paciente_id}/atendimento/retomar", response_model=AtendimentoStatus)
def retomar_atendimento(
    paciente_id: int, db: DbDep, colaborador: MedicoAtual
) -> AtendimentoStatus:
    prontuario = _get_prontuario(paciente_id, db)
    return _transicionar(
        prontuario,
        db,
        colaborador,
        de="aguardando_exames",
        para="em_atendimento",
        tipo_evolucao="Retomada de Atendimento",
        descricao="Atendimento retomado após exames complementares.",
    )
