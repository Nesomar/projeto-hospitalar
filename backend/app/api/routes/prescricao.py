from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import DbDep, get_prontuario_ativo, require_perfil
from app.models.colaborador import Colaborador
from app.models.evolucao import Evolucao
from app.models.prescricao import Prescricao
from app.schemas.prescricao import PrescricaoCreate, PrescricaoOut

router = APIRouter(prefix="/api", tags=["prescricao"])

MedicoAtual = Annotated[Colaborador, Depends(require_perfil("medico"))]


@router.post(
    "/pacientes/{paciente_id}/prescricoes",
    response_model=PrescricaoOut,
    status_code=status.HTTP_201_CREATED,
)
def prescrever(
    paciente_id: int,
    payload: PrescricaoCreate,
    db: DbDep,
    colaborador: MedicoAtual,
) -> Prescricao:
    prontuario = get_prontuario_ativo(paciente_id, db)

    prescricao = Prescricao(
        prontuario_id=prontuario.id,
        medicamento=payload.medicamento,
        dosagem=payload.dosagem,
        via=payload.via,
        frequencia=payload.frequencia,
        observacoes=payload.observacoes,
        responsavel_matricula=colaborador.matricula,
    )
    db.add(prescricao)
    db.flush()

    evolucao = Evolucao(
        prontuario_id=prontuario.id,
        tipo="Prescrição",
        descricao=f"Prescrito {payload.medicamento} {payload.dosagem} — {payload.via}.",
        responsavel_matricula=colaborador.matricula,
    )
    db.add(evolucao)
    db.commit()
    db.refresh(prescricao)

    return prescricao
