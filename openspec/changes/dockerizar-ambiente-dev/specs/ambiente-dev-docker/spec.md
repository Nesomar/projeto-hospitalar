## ADDED Requirements

### Requirement: Subida completa do ambiente com um único comando
O sistema SHALL permitir que Postgres, backend (FastAPI) e frontend (Vite) subam prontos pra uso
com um único comando `docker compose up`, sem exigir passo manual adicional (venv, `npm install`,
migration ou seed rodados à parte).

#### Scenario: Primeira subida em um clone novo do repositório
- **WHEN** o usuário roda `docker compose up` em um clone novo (sem volumes Docker prévios)
- **THEN** os três serviços (`postgres`, `backend`, `frontend`) sobem saudáveis, o schema do banco
  fica atualizado na `head` do Alembic, e a API responde em `http://localhost:8000/docs`

#### Scenario: Frontend acessível a partir do host
- **WHEN** o serviço `frontend` está rodando dentro do container
- **THEN** `http://localhost:5173` é acessível a partir do navegador no host (Windows), servindo a
  aplicação React

### Requirement: Administrador inicial disponível sem passo manual
O sistema SHALL garantir que, após `docker compose up`, exista um colaborador com matrícula
`000001`, perfil `administrador` e PIN `1234`, pronto pra login, sem exigir execução manual de
script de seed.

#### Scenario: Login imediato após subir o ambiente
- **WHEN** o usuário acessa o frontend e faz login com matrícula `000001` / PIN `1234` logo após
  `docker compose up` concluir
- **THEN** o login é aceito e o usuário acessa a tela de administrador

#### Scenario: Reinício do container backend não falha por matrícula já existente
- **WHEN** o container `backend` é reiniciado (ex.: `docker compose restart backend`) e a
  matrícula `000001` já existe no banco
- **THEN** o container inicia normalmente e a API fica disponível, sem o processo de entrypoint
  falhar por causa do seed

### Requirement: Hot-reload preservado em ambos os serviços
O sistema SHALL refletir alterações de código feitas no host, dentro dos containers em execução,
sem exigir rebuild de imagem.

#### Scenario: Alteração em arquivo Python do backend
- **WHEN** um arquivo dentro de `backend/app/` é salvo no host enquanto o container `backend` está
  rodando
- **THEN** o `uvicorn` recarrega automaticamente e a mudança fica visível na próxima requisição,
  sem `docker compose restart`

#### Scenario: Alteração em componente React do frontend
- **WHEN** um arquivo dentro de `frontend/src/` é salvo no host enquanto o container `frontend`
  está rodando
- **THEN** o Vite aplica Hot Module Replacement e a mudança aparece no navegador sem reload manual
  da página

### Requirement: Isolamento de dependências entre host e container
O sistema SHALL manter as dependências instaladas (pacotes Python do backend, `node_modules` do
frontend) isoladas dentro de cada container, sem depender de instalação prévia no host nem sofrer
conflito de binários nativos entre Windows e Linux.

#### Scenario: Clone novo sem `.venv` nem `node_modules` no host
- **WHEN** o repositório é clonado do zero, sem `backend/.venv` nem `frontend/node_modules`
  presentes no host
- **THEN** `docker compose up` funciona normalmente, pois as dependências são instaladas dentro da
  imagem/volume do container durante o build

#### Scenario: `.venv` ou `node_modules` pré-existentes no host, instalados para Windows
- **WHEN** o host já tem `backend/.venv` ou `frontend/node_modules` instalados nativamente pra
  Windows
- **THEN** o container ainda assim usa suas próprias dependências (via volume nomeado), sem
  conflito de binário nativo incompatível
