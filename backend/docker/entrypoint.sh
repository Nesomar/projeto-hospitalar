#!/bin/sh
set -e

alembic upgrade head

python scripts/seed_colaborador.py --matricula 000001 --pin 1234 --nome "Admin Sistema" --perfil administrador || true

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
