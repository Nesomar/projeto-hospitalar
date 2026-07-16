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

- Python 3.11+
- Node.js 18+
- Docker (roda o PostgreSQL via `docker-compose.yml`) — ou SQLite para um teste rápido sem Docker

## Backend

### 1. Ambiente virtual e dependências

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements-dev.txt
```

### 2. Banco de dados

Copie `.env.example` para `.env` e ajuste `JWT_SECRET` (mínimo 32 caracteres, sem valor padrão inseguro):

```bash
cp .env.example .env
```

**Opção A — PostgreSQL via Docker Compose (recomendado, reflete o schema real):**

```bash
docker compose up -d      # a partir da raiz do repositório
cd backend
alembic upgrade head
```

**Opção B — SQLite (rápido, sem Docker/Postgres instalado):**

Edite `DATABASE_URL` no `.env` para `sqlite:///./dev.db` e crie as tabelas diretamente
(o Alembic aqui foi escrito para Postgres; para SQLite use o metadata do SQLAlchemy):

```bash
python -c "from app.core.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"
```

### 3. Criar o primeiro administrador

O cadastro de enfermeiros e médicos (`POST /api/colaboradores`) exige um administrador autenticado,
então o primeiro administrador precisa ser criado direto no banco via script de bootstrap:

```bash
python scripts/seed_colaborador.py --matricula 000001 --pin 1234 --nome "Admin Sistema" --perfil administrador
```

Depois, faça login com essa matrícula/PIN no frontend e cadastre enfermeiros/médicos pela tela
"Gestão de Colaboradores" (ou direto via `POST /api/colaboradores`, autenticado como administrador).
O script também pode ser usado pra criar enfermeiro/médico direto no banco, se preferir pular a UI:

```bash
python scripts/seed_colaborador.py --matricula 000002 --pin 5678 --nome "Enf. Carla Nunes" --perfil enfermeiro
python scripts/seed_colaborador.py --matricula 000003 --pin 9012 --nome "Dr. Ricardo Alves" --perfil medico
```

### 4. Rodar a API

```bash
uvicorn app.main:app --reload --port 8000
```

Docs interativas em `http://localhost:8000/docs`.

### 5. Rodar os testes

```bash
pytest
```

## Frontend

```bash
cd frontend
npm install
cp .env.example .env   # aponta para http://localhost:8000 por padrão
npm run dev
```

Acesse `http://localhost:5173`. Login com as credenciais do administrador criadas no passo 3
(matrícula `000001` / PIN `1234`) pra cadastrar enfermeiros/médicos, ou com as credenciais
de um enfermeiro/médico já cadastrado.

## Estrutura do repositório

```
backend/            API FastAPI, models, schemas, testes, migrations Alembic
frontend/            React + Vite
docs/                SRD, casos de uso, modelo de dados, protótipo de referência
openspec/            Changes formais (specs e tasks por fase de implementação)
docker-compose.yml   PostgreSQL local para desenvolvimento
```
