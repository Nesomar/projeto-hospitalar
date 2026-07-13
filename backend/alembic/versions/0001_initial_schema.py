"""Fundacao de dados: COLABORADOR, PACIENTE, PRONTUARIO, EVOLUCAO, PRESCRICAO

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-13

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

perfil_colaborador = sa.Enum("enfermeiro", "medico", name="perfil_colaborador")
classificacao_risco = sa.Enum(
    "vermelho", "laranja", "amarelo", "verde", "azul", name="classificacao_risco"
)
via_prescricao = sa.Enum("Oral", "IV", "IM", "SC", "Tópica", name="via_prescricao")


def upgrade() -> None:
    bind = op.get_bind()
    perfil_colaborador.create(bind, checkfirst=True)
    classificacao_risco.create(bind, checkfirst=True)
    via_prescricao.create(bind, checkfirst=True)

    op.create_table(
        "colaboradores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("matricula", sa.String(6), nullable=False, unique=True),
        sa.Column("pin_hash", sa.String, nullable=False),
        sa.Column("nome", sa.String, nullable=False),
        sa.Column("perfil", perfil_colaborador, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_colaboradores_matricula", "colaboradores", ["matricula"])

    op.create_table(
        "pacientes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String, nullable=False),
        sa.Column("cpf", sa.String(11), nullable=False, unique=True),
        sa.Column("cns", sa.String(15), nullable=True, unique=True),
        sa.Column("data_nascimento", sa.Date, nullable=False),
        sa.Column("sexo", sa.String, nullable=True),
        sa.Column("telefone", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_pacientes_cpf", "pacientes", ["cpf"])

    op.create_table(
        "prontuarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("paciente_id", sa.Integer, sa.ForeignKey("pacientes.id"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("classificacao_risco", classificacao_risco, nullable=True),
        sa.Column("pas", sa.Integer, nullable=True),
        sa.Column("pad", sa.Integer, nullable=True),
        sa.Column("fc", sa.Integer, nullable=True),
        sa.Column("fr", sa.Integer, nullable=True),
        sa.Column("temp", sa.Float, nullable=True),
        sa.Column("spo2", sa.Integer, nullable=True),
        sa.Column("dor", sa.Integer, nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_prontuarios_paciente_id", "prontuarios", ["paciente_id"])

    op.create_table(
        "evolucoes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("prontuario_id", sa.Integer, sa.ForeignKey("prontuarios.id"), nullable=False),
        sa.Column("data", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("tipo", sa.String, nullable=False),
        sa.Column("descricao", sa.String, nullable=False),
        sa.Column("responsavel_matricula", sa.String(6), sa.ForeignKey("colaboradores.matricula"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_evolucoes_prontuario_id", "evolucoes", ["prontuario_id"])

    op.create_table(
        "prescricoes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("prontuario_id", sa.Integer, sa.ForeignKey("prontuarios.id"), nullable=False),
        sa.Column("data", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("medicamento", sa.String, nullable=False),
        sa.Column("dosagem", sa.String, nullable=False),
        sa.Column("via", via_prescricao, nullable=False),
        sa.Column("frequencia", sa.String, nullable=True),
        sa.Column("observacoes", sa.String, nullable=True),
        sa.Column("responsavel_matricula", sa.String(6), sa.ForeignKey("colaboradores.matricula"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_prescricoes_prontuario_id", "prescricoes", ["prontuario_id"])


def downgrade() -> None:
    op.drop_table("prescricoes")
    op.drop_table("evolucoes")
    op.drop_table("prontuarios")
    op.drop_table("pacientes")
    op.drop_table("colaboradores")

    bind = op.get_bind()
    via_prescricao.drop(bind, checkfirst=True)
    classificacao_risco.drop(bind, checkfirst=True)
    perfil_colaborador.drop(bind, checkfirst=True)
