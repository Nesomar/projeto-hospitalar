# SPEC.md - Contrato de Desenvolvimento (SDD)

## 1. Visão Geral e Resultados Esperados
Este documento é a ÚNICA fonte de verdade para a orquestração do desenvolvimento. O objetivo é construir um sistema hospitalar seguro e em conformidade com a LGPD.

### Objetivos de Alto Nível
- [x] Implementar autenticação via matrícula e PIN.
- [x] Gerenciar cadastro de pacientes (CNS/CPF).
- [x] Garantir trilhas de auditoria imutáveis.

## 2. Contexto do Projeto (Documentação Imutável)
As definições detalhadas estão distribuídas nos seguintes documentos:
- [Visão](01-visao.md)
- [Requisitos](02-requisitos.md)
- [Casos de Uso](03-casos-uso.md)
- [Modelo de Dados](04-modelo-dados.md)
- [Interfaces](05-interfaces.md)
- [Arquitetura](06-arquitetura.md)
- [Glossário](07-glossario.md)

## 3. Limites de Escopo e Guardrails (Anti-Patterns)
**A IA DEVE:**
- Seguir rigorosamente o Modelo de Dados definido em `04-modelo-dados.md`.
- Implementar testes unitários para cada funcionalidade nova.
- Utilizar criptografia AES-256 para dados sensíveis.

**A IA NÃO DEVE:**
- Criar dependências externas não documentadas em `06-arquitetura.md`.
- Implementar exclusão física de registros (usar Soft Delete).
- Burlar o sistema de RBAC (Role-Based Access Control).

## 4. Task Breakdown (Plano de Implementação)
Plano detalhado e fase-a-fase em `openspec/changes/auth-matricula-pin-srd/tasks.md`
(mudança `auth-matricula-pin-srd`). Resumo do progresso:

- [x] Fase 1 — Fundação de Dados: migrations Alembic (`COLABORADOR`, `PACIENTE`, `PRONTUARIO`,
  `EVOLUCAO`, `PRESCRICAO`), soft delete e enum de `classificacao_risco`.
- [x] Fase 2 — Autenticação (RF001): login por matrícula + PIN (hash bcrypt), JWT, RBAC por perfil.
- [x] Fase 3 — Cadastro de Paciente (RF002): `POST /api/pacientes` com validação CPF/CNS,
  evolução automática "Cadastro".
- [x] Fase 4 — Triagem (Protocolo de Manchester, UC001): cálculo/confirmação de classificação de
  risco, 5 cores com cascata de critérios.
- [x] Fase 5 — Prontuário (UC002): consulta somente-leitura (sinais vitais, evolução, prescrições).
- [x] Fase 6 — Prescrição (UC003): `POST /api/pacientes/{id}/prescricoes` restrito a perfil médico.
- [x] Fase 7 — Painel de Atendimento (UC006): listagem priorizada por gravidade, filtro por cor.
- [x] Fase 8 — Front-end: React (Vite) recriando as telas do protótipo com chamadas reais à API.
- [ ] Fase 9 — Fechamento: validação das specs, sincronização deste documento (em andamento),
  arquivamento da mudança pendente de validação em produção/homologação.

## 5. Critérios de Verificação Global
- [x] Cobertura de testes nas rotas de autenticação, RBAC, cadastro, triagem, prontuário,
  prescrição e painel (`backend/tests/`, 69 testes).
- [ ] Zero vulnerabilidades críticas no lint de segurança — nenhuma varredura SAST formal rodada
  ainda; pendente para antes de produção.
- [ ] Criptografia AES-256 para dados sensíveis em repouso (RNF001) — **não implementada**. Apenas
  o PIN é protegido (hash bcrypt); CPF/CNS/demais campos ficam em texto plano no PostgreSQL. Gap
  conhecido, deve ser tratado antes de uso em produção.
- [x] Documentação OpenAPI gerada automaticamente pelo FastAPI (`/docs`, `/openapi.json`).
