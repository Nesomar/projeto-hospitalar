# UPA Nordeste — Sistema de Triagem Hospitalar

Sistema de atendimento hospitalar (cadastro de paciente, triagem pelo Protocolo de Manchester,
prontuário, prescrição e painel de atendimento). Projeto doc-driven — veja `docs/` e `openspec/`
para especificação e decisões de arquitetura.

## Stack

- **Back-end**: Python / FastAPI (`backend/`)
- **Banco de dados**: PostgreSQL, schema versionado via Alembic
- **Front-end**: React + Vite (`frontend/`)
- **Autenticação**: matrícula (6 dígitos) + PIN (4 dígitos), JWT

## Pré-requisitos

- Docker + Docker Compose (única dependência pra rodar o projeto local)

## Rodando local (via Docker Compose — recomendado)

```bash
cp backend/.env.example backend/.env      # ajuste JWT_SECRET (mínimo 32 caracteres)
cp frontend/.env.example frontend/.env
docker compose up
```

Isso sobe três serviços:

- **postgres** — banco de dados, com schema já atualizado (`alembic upgrade head` roda automático)
- **backend** — API FastAPI em `http://localhost:8000` (docs em `/docs`), com hot-reload
- **frontend** — React + Vite em `http://localhost:5173`, com hot-reload

Um administrador já fica pronto pro primeiro login: matrícula `000001` / PIN `1234`. Acesse
`http://localhost:5173`, faça login com essas credenciais e cadastre enfermeiros/médicos pela tela
"Gestão de Colaboradores".

Editar código em `backend/` ou `frontend/` no host reflete direto nos containers (volume mount) —
não precisa rebuildar imagem no dia a dia. Rebuild só é necessário depois de mudar dependências
(`requirements.txt`/`requirements-dev.txt` ou `package.json`).

> **Nota:** o hot-reload usa polling (necessário pro bind mount funcionar no Docker Desktop com
> WSL2 no Windows), então uma mudança salva pode levar ~15-20s pra refletir no container, em vez
> de ser instantânea.

```bash
docker compose build backend    # ou frontend
```

### Comandos pontuais

```bash
docker compose exec backend pytest                      # testes
docker compose exec frontend npm run lint                # lint do frontend
docker compose exec backend python scripts/seed_colaborador.py \
  --matricula 000002 --pin 5678 --nome "Enf. Carla Nunes" --perfil enfermeiro
```

## Rodando sem Docker (alternativa manual)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements-dev.txt
cp .env.example .env          # ajuste JWT_SECRET
```

Banco de dados — Postgres via Docker (só o container do banco, sem os outros serviços) ou SQLite:

```bash
docker compose up -d postgres      # a partir da raiz do repositório
cd backend
alembic upgrade head
```

Ou, pra um teste rápido sem Docker/Postgres instalado, edite `DATABASE_URL` no `.env` para
`sqlite:///./dev.db` e crie as tabelas direto pelo metadata do SQLAlchemy (o Alembic aqui foi
escrito para Postgres):

```bash
python -c "from app.core.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"
```

Criar o primeiro administrador (necessário pois `POST /api/colaboradores` exige autenticação):

```bash
python scripts/seed_colaborador.py --matricula 000001 --pin 1234 --nome "Admin Sistema" --perfil administrador
```

Rodar a API e os testes:

```bash
uvicorn app.main:app --reload --port 8000
pytest
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # aponta para http://localhost:8000 por padrão
npm run dev
```

Acesse `http://localhost:5173` e faça login com o administrador criado acima (`000001` / `1234`).

## Estrutura do repositório

```
backend/            API FastAPI, models, schemas, testes, migrations Alembic
frontend/            React + Vite
docs/                SRD, casos de uso, modelo de dados, protótipo de referência
openspec/            Changes formais (specs e tasks por fase de implementação)
docker-compose.yml   Postgres + backend + frontend para desenvolvimento local
```
