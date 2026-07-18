#!/bin/sh
set -e

alembic upgrade head

python scripts/seed_colaborador.py \
  --matricula "${ADMIN_MATRICULA:-000001}" \
  --pin "${ADMIN_PIN:-1234}" \
  --nome "${ADMIN_NOME:-Admin Sistema}" \
  --perfil administrador || true

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
