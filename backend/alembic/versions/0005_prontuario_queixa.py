"""Adiciona queixa ao PRONTUARIO (queixa principal registrada na triagem)

Revision ID: 0005_prontuario_queixa
Revises: 0004_perfil_administrador
Create Date: 2026-10-03

"""
from alembic import op
import sqlalchemy as sa

revision = "0005_prontuario_queixa"
down_revision = "0004_perfil_administrador"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("prontuarios", sa.Column("queixa", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("prontuarios", "queixa")
