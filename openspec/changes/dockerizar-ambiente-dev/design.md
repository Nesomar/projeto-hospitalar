## Context

O `docker-compose.yml` atual só define o serviço `postgres`. Backend (FastAPI, `backend/`) e
frontend (React + Vite, `frontend/`) rodam hoje direto no host: venv Python + `.venv/`, e
`node_modules/` instalados no Windows. O fluxo documentado no `README.md` tem 8 passos manuais
espalhados em 2+ terminais antes do app subir (ver proposal.md).

Duas dependências têm binários nativos compilados por plataforma: `psycopg[binary]` (backend) e
`oxlint`/`lightningcss` (frontend, via Rust/native bindings do Vite 8 e do toolchain oxc). Isso
significa que `.venv`/`node_modules` instalados no Windows não funcionam se montados direto dentro
de um container Linux — é a armadilha mais comum ao dockerizar um projeto que já tem dependências
instaladas no host.

## Goals / Non-Goals

**Goals:**
- `docker compose up` sobe Postgres + backend + frontend prontos pra uso, sem passo manual
  adicional.
- Hot-reload preservado: editar código no host (VS Code, etc.) reflete no container rodando
  (`uvicorn --reload`, Vite HMR).
- Primeiro login (admin `000001`/`1234`) já funciona logo após o `up`, sem rodar script à parte.
- `pytest` e lint continuam disponíveis via `docker compose exec`.

**Non-Goals:**
- Dockerfile/compose de produção — este change cobre só desenvolvimento local.
- Migrar CI para rodar dentro dos containers (fora de escopo; não há CI configurado hoje).
- Alterar `scripts/seed_colaborador.py` — ele é reaproveitado como está.
- Suportar rodar sem Docker deixa de ser o caminho principal, mas o fluxo manual do README não é
  removido, só rebaixado a alternativa.

## Decisions

**1. Volume mount do código + volume nomeado só onde a dependência mora dentro de `/app`.**
`./backend:/app` e `./frontend:/app` montam o código pra hot-reload. O risco descrito originalmente
(dependência instalada dentro da imagem sendo sobrescrita pelo bind mount do host) só existe onde a
dependência é instalada *dentro* da árvore montada. No backend, `pip install` grava em
`/usr/local/lib/python3.11/site-packages` — fora de `/app` — então o bind mount não toca nisso;
nenhum volume extra é necessário. No frontend, `npm install` grava em `/app/node_modules`, dentro da
árvore montada, e `oxlint`/`lightningcss` têm binário nativo por plataforma — aí sim é preciso
`frontend-node-modules:/app/node_modules` como volume nomeado, que tem precedência sobre o bind
mount do pai e preserva o `node_modules` instalado no build da imagem (Linux) em vez do que existir
(ou não) em `./frontend/node_modules` no host.
Alternativa considerada: instalar dependências no host e montar tudo direto — descartada porque é
exatamente o problema atual (binários nativos incompatíveis entre Windows e Linux).

**2. Entrypoint do backend faz migration + seed + start, nessa ordem, todo boot.**
Um `entrypoint.sh` (novo arquivo, `backend/docker/entrypoint.sh` ou similar) roda:
`alembic upgrade head` → `python scripts/seed_colaborador.py --matricula 000001 --pin 1234 --nome
"Admin Sistema" --perfil administrador || true` → `exec uvicorn app.main:app --reload --host
0.0.0.0 --port 8000`.
O `|| true` absorve o exit code 2 que o script já dá quando a matrícula existe (comportamento atual,
não alterado — ver proposal.md). `alembic upgrade head` é naturalmente idempotente (não faz nada se
já estiver na head). Alternativa considerada: tornar o script idempotente (checar existência antes
de dar erro) — descartada porque isso é mudança de comportamento de um script usado também
manualmente pelo usuário final (README seção 3), e não é o que foi pedido; a orquestração é o lugar
certo pra absorver esse exit code, não a lógica do script.

**3. `depends_on` com `condition: service_healthy` pro backend aguardar o Postgres.**
O `healthcheck` do serviço `postgres` já existe no compose. Backend usa
`depends_on: postgres: condition: service_healthy` — evita corrida em que `alembic upgrade head`
roda antes do Postgres aceitar conexões (problema comum em `docker compose up` a frio).

**4. Vite com `server: { host: true }` em vez de flag de linha de comando.**
Configurar no `vite.config.js` (não só `vite --host 0.0.0.0` no `command:` do compose) mantém o
comportamento correto também pra quem roda `npm run dev` fora do Docker (fluxo manual do README
continua funcionando igual). Efeito colateral nenhum: `host: true` só faz o dev server escutar em
todas as interfaces, não muda porta nem comportamento de build.

**5. Dois `Dockerfile`s de dev simples (não multi-stage).**
`backend/Dockerfile` (`python:3.11-slim`, `pip install -r requirements-dev.txt`) e
`frontend/Dockerfile` (`node:20-slim`, `npm install`) — sem multi-stage, sem otimização de camada
pra produção, porque não é o objetivo deste change (ver Non-Goals). Simplicidade > otimização
prematura pra um ambiente que é recriado raramente e usado só localmente.

**6. Polling forçado pra file-watching (`WATCHFILES_FORCE_POLLING` no backend,
`server.watch.usePolling` no Vite) — descoberto durante validação (tasks 5.4/5.5).**
Bind mount de pasta Windows através do Docker Desktop (WSL2) não propaga eventos `inotify` — nem
`uvicorn --reload` nem o watcher padrão do Vite (chokidar) detectavam mudança de arquivo sem isso.
Com polling forçado, a detecção funciona, mas com latência de ~15-20s (não instantânea) — o poll
varre o diretório periodicamente em vez de reagir a evento do filesystem. Aceitável pra este
change (hot-reload "funciona sem restart manual" é o requisito da spec, não "é instantâneo"), mas
documentado no README como limitação conhecida. Alternativa não testada: Docker Desktop com
"VirtioFS" em vez do backend de compartilhamento de arquivo padrão pode propagar eventos nativos e
dispensar o polling — fica como possível otimização futura, fora de escopo agora.

## Risks / Trade-offs

- **Volume nomeado fica "preso" na primeira instalação** → se `requirements-dev.txt` ou
  `package.json` mudar depois, o volume nomeado não atualiza sozinho. Mitigação: documentar no
  README que `docker compose build` (ou `down -v` + `up` pro caso extremo) é necessário depois de
  mudar dependências — mesma mecânica que já existe hoje pra quem esquece `pip install`/`npm
  install` depois de um `git pull`.
- **Primeira subida (`docker compose up` a frio) demora mais** (build de 2 imagens + install de
  dependências) → aceitável, é custo único; builds seguintes usam cache de camada do Docker.
- **Seed do admin roda a cada restart do container** → custo desprezível (uma query + `|| true`),
  mas se o schema do banco mudar de forma incompatível com o script antigo (ex.: coluna renomeada),
  o erro fica silencioso pelo `|| true`. Mitigação: não é um risco novo — o `alembic upgrade head`
  já garante que o schema está atualizado antes do seed rodar; se o script quebrar por outro motivo,
  fica visível no log do container mesmo com exit code absorvido (nenhum `2>&1 > /dev/null`
  aplicado, só o exit code é ignorado).
- **Credenciais de dev com default fixo** (Postgres `upa_user`/`upa_password`, admin
  `000001`/`1234`) → sinalizado por review automática de segurança como "hardcoded-credentials".
  São valores de desenvolvimento local, não secrets de produção (mesmo padrão que já existia no
  `docker-compose.yml` original, antes deste change, pro serviço `postgres`). Mitigação aplicada:
  extraídos pra variáveis de ambiente com default (`${POSTGRES_PASSWORD:-upa_password}` no compose,
  `${ADMIN_PIN:-1234}` no entrypoint), documentadas em `.env.example` (raiz) — elimina a duplicação
  literal da senha em dois lugares do compose e permite sobrescrever sem editar código versionado.
  Não removido o default: sem ele, `docker compose up` deixaria de ser um comando único (voltaria a
  exigir configurar credenciais antes de subir), contrariando o objetivo central do change.
- **Containers rodam como root** (sem `USER` nos Dockerfiles) → sinalizado por review automática
  como "container-privilege". Decisão: mantido de propósito. Rodar como usuário não-root exigiria
  alinhar UID/GID do container com o do host pra escrita no bind mount (`./backend:/app`,
  `./frontend:/app`) funcionar sem erro de permissão — variável por máquina/SO (especialmente
  Windows), adicionando complexidade real sem benefício de segurança nesse contexto: os containers
  só existem na máquina do próprio desenvolvedor, não recebem tráfego externo nem dados de
  terceiros. Hardening de container (`USER`, capabilities, read-only rootfs) é hardening de
  produção — explicitamente fora de escopo (ver Non-Goals). Revisitar se este compose algum dia for
  reusado como base pra imagem publicada ou ambiente compartilhado.

## Migration Plan

1. Criar `backend/Dockerfile` + `backend/docker/entrypoint.sh`.
2. Criar `frontend/Dockerfile`.
3. Editar `frontend/vite.config.js` (`server: { host: true }`).
4. Editar `docker-compose.yml`: adicionar serviços `backend` e `frontend`, volumes nomeados,
   `depends_on` com healthcheck.
5. Testar `docker compose up` do zero (sem volumes prévios) — validar migration, seed, hot-reload
   nos dois serviços, acesso via `localhost:8000/docs` e `localhost:5173`.
6. Atualizar `README.md`.
Sem rollback formal necessário — é aditivo ao `docker-compose.yml` existente; quem preferir o fluxo
manual antigo continua podendo seguir as instruções secundárias do README.

## Open Questions

Nenhuma pendente — decisões de hot-reload, seed automático e isolamento de dependências já
confirmadas com o usuário durante o explore.
