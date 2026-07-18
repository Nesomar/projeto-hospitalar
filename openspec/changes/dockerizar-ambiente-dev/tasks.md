## 1. Backend containerizado

- [x] 1.1 Criar `backend/Dockerfile` (`python:3.11-slim`, copia `requirements-dev.txt`, `pip
      install`, copia código)
- [x] 1.2 Criar `backend/docker/entrypoint.sh`: `alembic upgrade head` → seed idempotente do admin
      (`scripts/seed_colaborador.py --matricula 000001 --pin 1234 --nome "Admin Sistema" --perfil
      administrador || true`) → `exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [x] 1.3 Garantir que `entrypoint.sh` tem permissão de execução (`chmod +x` no Dockerfile ou no
      próprio arquivo antes do commit)

## 2. Frontend containerizado

- [x] 2.1 Criar `frontend/Dockerfile` (`node:20-slim`, `npm install`, copia código, `CMD ["npm",
      "run", "dev"]`)
- [x] 2.2 Editar `frontend/vite.config.js`: adicionar `server: { host: true }`

## 3. Orquestração no docker-compose.yml

- [x] 3.1 Adicionar serviço `backend`: build a partir de `backend/Dockerfile`, `env_file:
      backend/.env` (com `DATABASE_URL` sobrescrito pra apontar pro host `postgres` da rede
      Docker), volume `./backend:/app` (sem volume nomeado extra — `pip install` grava fora de
      `/app`, ver design.md), porta `8000:8000`, `depends_on: postgres: condition:
      service_healthy`
- [x] 3.2 Adicionar serviço `frontend`: build a partir de `frontend/Dockerfile`, `env_file:
      frontend/.env`, volumes `./frontend:/app` + volume nomeado
      `frontend-node-modules:/app/node_modules`, porta `5173:5173`, `depends_on: backend`
- [x] 3.3 Declarar o volume nomeado novo (`frontend-node-modules`) na seção `volumes:` do compose

## 4. Documentação

- [x] 4.1 Atualizar `README.md`: novo fluxo principal via `docker compose up` (pré-requisitos,
      passo único, onde acessar backend/frontend, credenciais do admin já seedado)
- [x] 4.2 Documentar no `README.md` os comandos pontuais via container (`docker compose exec
      backend pytest`, `docker compose exec backend python scripts/seed_colaborador.py ...` pra
      criar enfermeiro/médico adicional, `docker compose build` após mudar dependências)
- [x] 4.3 Manter o fluxo manual (venv/npm local) documentado como alternativa secundária, não como
      passo principal

## 5. Validação

- [x] 5.1 Rodar `docker compose down -v` (limpar estado local) seguido de `docker compose up` do
      zero e confirmar: os 3 serviços sobem saudáveis, `alembic upgrade head` aplica o schema,
      `http://localhost:8000/docs` responde
- [x] 5.2 Confirmar login com matrícula `000001` / PIN `1234` funciona no frontend
      (`http://localhost:5173`) logo após o `up`, sem rodar seed manualmente
- [x] 5.3 Rodar `docker compose restart backend` com a matrícula `000001` já existente e confirmar
      que o container volta a ficar saudável (seed idempotente não derruba o entrypoint)
- [x] 5.4 Editar um arquivo em `backend/app/` e confirmar reload automático do `uvicorn` nos logs
      do container. Achado: bind mount Windows→Docker Desktop (WSL2) não emite eventos inotify;
      precisou `WATCHFILES_FORCE_POLLING=true` no serviço `backend` do compose. Mesmo com
      polling, reload leva ~15-20s (não é instantâneo) — documentado no README como limitação
      conhecida.
- [x] 5.5 Editar um arquivo em `frontend/src/` e confirmar HMR do Vite no navegador. Mesmo achado
      do 5.4: precisou `server.watch.usePolling: true` no `vite.config.js`, mesma latência de
      detecção.
- [x] 5.6 Rodar `docker compose exec backend pytest` e confirmar que a suíte de testes passa igual
      ao fluxo manual anterior — 102 passed.
