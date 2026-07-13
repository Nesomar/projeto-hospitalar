# CLAUDE.md

Guia pro Claude Code trabalhar neste repositório (projeto UPA Nordeste — sistema de triagem hospitalar).

## Visão geral

Projeto doc-driven (SDD/OpenSpec). O SRD vive em `docs/`, o protótipo de referência (HTML/JS mockado) em
`docs/prototipo/projeto/Prototipo Hospitalar.dc.html`, e as mudanças formais em `openspec/changes/`.
A implementação real do backend vive em `backend/`.

## Stack

- **Front-end**: React (componentes funcionais, hooks) — protótipo de referência já define o comportamento.
- **Back-end**: Python / FastAPI, em `backend/`.
- **Banco de dados**: PostgreSQL, schema versionado via Alembic (`backend/alembic/`), models em `backend/app/models/`.
- **Autenticação**: matrícula (6 dígitos) + PIN (4 dígitos), hash bcrypt/argon2, JWT — ver `docs/06-arquitetura.md` e `openspec/changes/auth-matricula-pin-srd/`.

## Fluxo de trabalho por fase (acordo fixo — 2026-07-13)

O plano de implementação está em `openspec/changes/<change>/tasks.md`, organizado em fases numeradas.
Para **cada fase**, seguir sempre esta sequência, sem pular etapas:

1. **Antes de começar a fase**: criar uma branch nova a partir de `develop` (uma branch por fase, não uma
   branch única pro change inteiro).
2. **Durante a implementação**: usar as skills de `fullstack-dev-skills` (ex.: `fastapi-expert`, `postgres-pro`,
   `python-pro`, `react-expert`, conforme a stack tocada na fase).
3. **Ao finalizar a implementação da fase**: rodar a skill `code-review` sobre o diff antes de considerar a
   fase concluída.
4. **Ao abrir PR**: usar `pr-review-toolkit` (skill `review-pr` / agentes do toolkit) em vez do fluxo de PR
   genérico.
5. **Trabalho de design/front-end**: usar `frontend-design` junto com `ui-ux-pro-max`.

Depois do merge de cada PR, sincronizar `develop` local (`git checkout develop && git pull`) antes de criar a
branch da próxima fase.

## Guardrails (ver `docs/06-arquitetura.md`)

- **Proibido `DELETE` físico** — soft delete via coluna `deleted_at` em todas as tabelas.
- **Proibido secret em código** — configuração sensível (`DATABASE_URL`, `JWT_SECRET`) só via `.env`/variáveis
  de ambiente, sem default inseguro no código (`Settings` do Pydantic deve exigir esses campos, nunca ter
  fallback tipo `"change-me"`).
- **Sem refactor não pedido** em arquivos de infraestrutura/configuração global.
- `classificacao_risco` restrito ao enum `vermelho|laranja|amarelo|verde|azul` (Protocolo de Manchester).
- `responsavel_matricula` é sempre FK obrigatória pra `COLABORADOR.matricula` (rastreabilidade de quem
  registrou cada evolução/prescrição).

## Onde olhar antes de implementar

- `docs/04-modelo-dados.md` — schema de dados e dicionário.
- `docs/03-casos-uso.md` — casos de uso (ex. UC001 = cálculo de Manchester).
- `openspec/changes/<change>/design.md` e `specs/*/spec.md` — decisões e cenários testáveis da mudança ativa.
- `openspec/changes/<change>/tasks.md` — checklist de implementação, fase a fase.
