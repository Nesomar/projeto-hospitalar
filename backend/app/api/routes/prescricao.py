from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbDep, require_perfil
from app.models.colaborador import Colaborador
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prescricao import Prescricao
from app.models.prontuario import Prontuario
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
