from fastapi import APIRouter, HTTPException, status

from app.api.deps import ClinicoAtual, DbDep
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prescricao import Prescricao
from app.models.prontuario import Prontuario
from app.schemas.prontuario import ProntuarioResponse, SinaisVitaisAtuais

router = APIRouter(prefix="/api", tags=["prontuario"])


@router.get("/pacientes/{paciente_id}/prontuario", response_model=ProntuarioResponse)
def consultar_prontuario(
    paciente_id: int,
    db: DbDep,
    colaborador: ClinicoAtual,
) -> ProntuarioResponse:
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

    evolucoes = (
        db.query(Evolucao)
        .filter(Evolucao.prontuario_id == prontuario.id, Evolucao.deleted_at.is_(None))
        .order_by(Evolucao.data.desc(), Evolucao.id.desc())
        .all()
    )
    prescricoes = (
        db.query(Prescricao)
        .filter(Prescricao.prontuario_id == prontuario.id, Prescricao.deleted_at.is_(None))
        .order_by(Prescricao.data.desc(), Prescricao.id.desc())
        .all()
    )

    return ProntuarioResponse(
        paciente_id=paciente.id,
        paciente_nome=paciente.nome,
        sinais_vitais=SinaisVitaisAtuais(
            classificacao_risco=prontuario.classificacao_risco,
            pas=prontuario.pas,
            pad=prontuario.pad,
            fc=prontuario.fc,
            fr=prontuario.fr,
            temp=prontuario.temp,
            spo2=prontuario.spo2,
            dor=prontuario.dor,
        ),
        evolucoes=evolucoes,
        prescricoes=prescricoes,
        pode_prescrever=colaborador.perfil == "medico",
    )
