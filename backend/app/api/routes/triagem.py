from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentColaborador, DbDep
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prontuario import Prontuario
from app.schemas.triagem import ConfirmarTriagemRequest, SinaisVitais, TriagemResultado
from app.services.manchester import calcular_manchester

router = APIRouter(prefix="/api", tags=["triagem"])


@router.post("/triagem/calcular", response_model=TriagemResultado)
def calcular_triagem(payload: SinaisVitais, _colaborador: CurrentColaborador) -> TriagemResultado:
    resultado = calcular_manchester(
        pas=payload.pas, fc=payload.fc, temp=payload.temp, spo2=payload.spo2, dor=payload.dor
    )
    return TriagemResultado(**resultado.__dict__)


@router.post("/pacientes/{paciente_id}/triagem/confirmar", response_model=TriagemResultado)
def confirmar_triagem(
    paciente_id: int,
    payload: ConfirmarTriagemRequest,
    db: DbDep,
    colaborador: CurrentColaborador,
) -> TriagemResultado:
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
    if prontuario.classificacao_risco is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Paciente já triado")

    resultado = calcular_manchester(
        pas=payload.pas, fc=payload.fc, temp=payload.temp, spo2=payload.spo2, dor=payload.dor
    )

    prontuario.classificacao_risco = resultado.cor
    prontuario.pas = payload.pas
    prontuario.pad = payload.pad
    prontuario.fc = payload.fc
    prontuario.fr = payload.fr
    prontuario.temp = payload.temp
    prontuario.spo2 = payload.spo2
    prontuario.dor = payload.dor

    queixa = payload.queixa or "sem queixa registrada"
    evolucao = Evolucao(
        prontuario_id=prontuario.id,
        tipo="Triagem",
        descricao=f"Classificação {resultado.cor} — {queixa}.",
        responsavel_matricula=colaborador.matricula,
    )
    db.add(evolucao)
    db.commit()

    return TriagemResultado(**resultado.__dict__)
