from typing import Literal

from fastapi import APIRouter

from app.api.deps import CurrentColaborador, DbDep
from app.models.paciente import Paciente
from app.models.prontuario import CLASSIFICACOES_RISCO, Prontuario
from app.schemas.painel import PainelItem

router = APIRouter(prefix="/api", tags=["painel"])

ORDEM_GRAVIDADE = {cor: indice for indice, cor in enumerate(CLASSIFICACOES_RISCO)}


@router.get("/painel", response_model=list[PainelItem])
def listar_painel(
    db: DbDep,
    colaborador: CurrentColaborador,
    cor: Literal[*CLASSIFICACOES_RISCO] | None = None,
) -> list[PainelItem]:
    registros = (
        db.query(Paciente, Prontuario)
        .join(Prontuario, Prontuario.paciente_id == Paciente.id)
        .filter(Paciente.deleted_at.is_(None), Prontuario.deleted_at.is_(None))
        .all()
    )

    itens = []
    for paciente, prontuario in registros:
        if cor is not None and prontuario.classificacao_risco != cor:
            continue
        status = "Aguardando Atendimento" if prontuario.classificacao_risco else "Aguardando Triagem"
        itens.append(
            PainelItem(
                paciente_id=paciente.id,
                nome=paciente.nome,
                classificacao_risco=prontuario.classificacao_risco,
                status=status,
                pode_fazer_triagem=colaborador.perfil == "enfermeiro" and status == "Aguardando Triagem",
            )
        )

    itens.sort(key=lambda item: ORDEM_GRAVIDADE.get(item.classificacao_risco, len(ORDEM_GRAVIDADE)))
    return itens
