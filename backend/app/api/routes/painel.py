from typing import Literal

from fastapi import APIRouter
from sqlalchemy import or_

from app.api.deps import CurrentColaborador, DbDep
from app.models.paciente import Paciente
from app.models.prontuario import CLASSIFICACOES_RISCO, Prontuario, status_efetivo
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
        .filter(
            Paciente.deleted_at.is_(None),
            Prontuario.deleted_at.is_(None),
            or_(Prontuario.status_atendimento.is_(None), Prontuario.status_atendimento != "alta"),
        )
        .all()
    )

    itens = []
    for paciente, prontuario in registros:
        if cor is not None and prontuario.classificacao_risco != cor:
            continue
        item_status = status_efetivo(prontuario)
        e_medico = colaborador.perfil == "medico"
        itens.append(
            PainelItem(
                paciente_id=paciente.id,
                nome=paciente.nome,
                classificacao_risco=prontuario.classificacao_risco,
                status=item_status,
                pode_fazer_triagem=colaborador.perfil == "enfermeiro"
                and item_status == "Aguardando Triagem",
                pode_iniciar_atendimento=e_medico and item_status == "Aguardando Atendimento",
                pode_dar_alta=e_medico and item_status == "Em Atendimento",
                pode_solicitar_exames=e_medico and item_status == "Em Atendimento",
                pode_retomar_atendimento=e_medico
                and item_status == "Aguardando Exames Complementares",
            )
        )

    itens.sort(key=lambda item: ORDEM_GRAVIDADE.get(item.classificacao_risco, len(ORDEM_GRAVIDADE)))
    return itens
