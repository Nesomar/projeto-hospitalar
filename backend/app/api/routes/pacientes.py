from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentColaborador, DbDep
from app.models.evolucao import Evolucao
from app.models.paciente import Paciente
from app.models.prontuario import Prontuario
from app.schemas.paciente import PacienteCreate, PacienteOut

router = APIRouter(prefix="/api", tags=["pacientes"])


@router.post("/pacientes", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(
    payload: PacienteCreate,
    db: DbDep,
    colaborador: CurrentColaborador,
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
