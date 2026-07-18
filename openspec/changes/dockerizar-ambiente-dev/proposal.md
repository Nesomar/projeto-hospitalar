## Why

Rodar o projeto localmente hoje exige 8 passos manuais em 2+ terminais (venv, pip install, copiar
`.env`, `alembic upgrade head`, seed manual do admin, `uvicorn`, `npm install`, `npm run dev`).
O `docker-compose.yml` atual só sobe o Postgres — backend e frontend ficam de fora do Docker, o
que é a origem da fricção. Um único `docker compose up` deve bastar pra ambiente completo de
desenvolvimento.

## What Changes

- Adicionar serviço `backend` ao `docker-compose.yml` (Dockerfile Python 3.11-slim), com volume
  mount do código (`./backend:/app`) pra hot-reload e volume nomeado separado pra dependências
  Python (evita colisão de binários nativos entre Windows-host e container Linux, ex.:
  `psycopg[binary]`).
- Adicionar serviço `frontend` ao `docker-compose.yml` (Dockerfile node:20-slim), com volume mount
  do código (`./frontend:/app`) e volume nomeado separado pro `node_modules` (mesma razão: `oxlint`
  e `lightningcss` têm binários nativos por plataforma).
- Entrypoint do backend: aguarda `postgres` healthy (healthcheck já existe) → `alembic upgrade
  head` → seed idempotente do admin bootstrap (matrícula `000001` / PIN `1234`, reaproveitando
  `scripts/seed_colaborador.py` sem alterá-lo — o entrypoint absorve o exit code de "já existe")
  → `uvicorn --reload --host 0.0.0.0`.
- `vite.config.js`: adicionar `server: { host: true }` (bind default é `localhost`, inacessível de
  fora do container).
- Atualizar `README.md`: seções "Backend" e "Frontend" passam a apontar pra `docker compose up`
  como fluxo principal; comandos pontuais (`pytest`, lint) documentados como
  `docker compose exec <serviço> <comando>`. Fluxo manual (venv/npm local) mantido como alternativa
  secundária pra quem não quiser Docker.

## Capabilities

### New Capabilities

- `ambiente-dev-docker`: ambiente de desenvolvimento local completo (Postgres + backend + frontend)
  orquestrado via `docker compose up`, com migration e seed de admin automáticos e hot-reload
  preservado.

### Modified Capabilities

(nenhuma — não há requisito de spec de produto sendo alterado)

## Impact

- **Código afetado**: `docker-compose.yml`, novos `backend/Dockerfile` e `frontend/Dockerfile`,
  novo script de entrypoint do backend, `frontend/vite.config.js`, `README.md`.
- **Não afetado**: lógica de aplicação (`app/`, componentes React), `scripts/seed_colaborador.py`
  (usado como está), testes (`pytest` continua rodando igual, só muda onde é invocado).
- **Fora de escopo**: Dockerfile de produção/deploy (não existe ainda) — este change cobre apenas
  ambiente de desenvolvimento local.
