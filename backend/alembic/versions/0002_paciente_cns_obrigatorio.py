"""Torna PACIENTE.cns obrigatorio (RF002 / spec cadastro-paciente)

Revision ID: 0002_paciente_cns_obrigatorio
Revises: 0001_initial_schema
Create Date: 2026-07-13

"""
from alembic import op
import sqlalchemy as sa

revision = "0002_paciente_cns_obrigatorio"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("pacientes", "cns", existing_type=sa.String(15), nullable=False)


def downgrade() -> None:
    op.alter_column("pacientes", "cns", existing_type=sa.String(15), nullable=True)
