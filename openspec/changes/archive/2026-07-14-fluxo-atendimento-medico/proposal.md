## Why

O fluxo de estado do paciente já está definido em `docs/03-casos-uso.md` (linha 87-94): Cadastro →
Aguardando Triagem → Aguardando Atendimento → Em Atendimento → fim. Mas o backend nunca implementou a
transição para "Em Atendimento": hoje `status` no painel (`painel.py:32`) é derivado só de
`classificacao_risco` (NULL/não-NULL), então existem apenas dois estados possíveis. Não há endpoint para o
médico iniciar atendimento, dar alta ou solicitar exames complementares — o médico pode prescrever para
qualquer paciente já triado, sem nenhum registro de que o atendimento de fato começou. Isso deixa o painel
sem visibilidade real de quem está sendo atendido, quem já teve alta e quem está aguardando exame, e sem
trilha de auditoria de quando o atendimento começou/terminou.

## What Changes

- Adiciona estado persistido de atendimento ao `Prontuario` (coluna nova), com transições explícitas
  restritas a perfil `medico`:
  - `Aguardando Atendimento` → `Em Atendimento` (ação "Iniciar Atendimento")
  - `Em Atendimento` → `Alta` (ação "Dar Alta") — estado terminal, some da listagem ativa do painel
  - `Em Atendimento` → `Aguardando Exames Complementares` (ação "Solicitar Exames") — permanece visível
  - `Aguardando Exames Complementares` → `Em Atendimento` (ação "Retomar Atendimento")
- Cada transição grava uma `Evolucao` (mesmo padrão de `triagem.py`/`prescricao.py`), com
  `responsavel_matricula` do médico que executou a ação.
- Painel de atendimento (`painel.py`, `PainelItem`) passa a expor os novos status e as ações disponíveis
  por paciente conforme perfil do usuário e status atual (similar a `pode_fazer_triagem` já existente).
- Alta remove o paciente da listagem ativa do painel (filtro por `deleted_at`/estado terminal, sem soft
  delete do registro — o prontuário continua consultável via UC002).
- Nova migration Alembic para a coluna de estado.

## Capabilities

### New Capabilities
- `atendimento-medico`: transições de estado do atendimento médico (iniciar atendimento, dar alta,
  solicitar exames complementares, retomar atendimento), restritas a perfil `medico`, com registro em
  evolução.

### Modified Capabilities
- `painel-atendimento`: painel passa a exibir os novos status (`Em Atendimento`,
  `Aguardando Exames Complementares`) e as ações condicionais correspondentes; pacientes com `Alta` saem
  da listagem ativa.

## Impact

- `backend/app/models/prontuario.py`: nova coluna de estado.
- `backend/alembic/`: nova migration.
- `backend/app/api/routes/`: novo router (ou extensão de rota existente) para as transições de
  atendimento; `painel.py` atualizado.
- `backend/app/schemas/painel.py`: `PainelItem` ganha campos de ação (ex.: `pode_iniciar_atendimento`,
  `pode_dar_alta`, `pode_solicitar_exames`, `pode_retomar_atendimento`).
- `openspec/specs/painel-atendimento/spec.md`: novos requirements/scenarios.
- Sem breaking changes em contratos existentes (triagem, prescrição, cadastro continuam iguais).
