"""Adiciona perfil administrador e coluna criado_por_matricula em COLABORADOR

Revision ID: 0004_perfil_administrador
Revises: 0003_status_atendimento
Create Date: 2026-07-15

Nota sobre downgrade: Postgres nao permite remover um valor de enum de forma
trivial (nao existe `ALTER TYPE ... DROP VALUE`). Por isso o downgrade() desta
migracao NAO reverte o `ADD VALUE 'administrador'` -- limitacao inerente ao
tipo enum do Postgres, nao uma escolha desta feature. A coluna
`criado_por_matricula` e revertida normalmente.
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_perfil_administrador"
down_revision = "0003_status_atendimento"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres 16 suporta ADD VALUE dentro de transacao desde a v12; o valor
    # novo so nao pode ser usado na mesma transacao em que foi criado, o que
    # nao acontece aqui.
    op.execute("ALTER TYPE perfil_colaborador ADD VALUE 'administrador'")
    op.add_column(
        "colaboradores",
        sa.Column(
            "criado_por_matricula",
            sa.String(6),
            sa.ForeignKey("colaboradores.matricula"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("colaboradores", "criado_por_matricula")
    # ALTER TYPE ... ADD VALUE nao suporta downgrade nativo no Postgres
    # (sem DROP VALUE). O valor 'administrador' permanece no enum.
