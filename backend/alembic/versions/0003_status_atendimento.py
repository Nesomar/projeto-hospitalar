"""Adiciona status_atendimento ao PRONTUARIO (fluxo pos-triagem)

Revision ID: 0003_status_atendimento
Revises: 0002_paciente_cns_obrigatorio
Create Date: 2026-07-14

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_status_atendimento"
down_revision = "0002_paciente_cns_obrigatorio"
branch_labels = None
depends_on = None

status_atendimento = sa.Enum(
    "em_atendimento", "aguardando_exames", "alta", name="status_atendimento"
)


def upgrade() -> None:
    status_atendimento.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "prontuarios",
        sa.Column("status_atendimento", status_atendimento, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("prontuarios", "status_atendimento")
    status_atendimento.drop(op.get_bind(), checkfirst=True)
