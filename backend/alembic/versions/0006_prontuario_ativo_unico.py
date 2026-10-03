"""Garante no maximo um atendimento ativo por paciente (indice unico parcial)

Revision ID: 0006_prontuario_ativo_unico
Revises: 0005_prontuario_queixa
Create Date: 2026-10-03

"""
from alembic import op

revision = "0006_prontuario_ativo_unico"
down_revision = "0005_prontuario_queixa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX uq_prontuario_ativo_por_paciente ON prontuarios (paciente_id) "
        "WHERE deleted_at IS NULL AND (status_atendimento IS NULL OR status_atendimento <> 'alta')"
    )


def downgrade() -> None:
    op.drop_index("uq_prontuario_ativo_por_paciente", table_name="prontuarios")
