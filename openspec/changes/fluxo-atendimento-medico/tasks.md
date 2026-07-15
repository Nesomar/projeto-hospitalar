## 1. Modelo de dados

- [x] 1.1 Adicionar coluna `status_atendimento` (enum nullable: `em_atendimento | aguardando_exames |
      alta`) em `backend/app/models/prontuario.py`
- [x] 1.2 Gerar migration Alembic para a coluna nova (`backend/alembic/versions/`)
- [x] 1.3 Rodar migration localmente e validar `alembic upgrade head` / `downgrade -1`

## 2. Endpoints de transição de atendimento

- [x] 2.1 Criar `backend/app/api/routes/atendimento.py` com router `MedicoAtual`
      (`require_perfil("medico")`, mesmo padrão de `prescricao.py`)
- [x] 2.2 Implementar `POST /api/pacientes/{id}/atendimento/iniciar` (valida
      `classificacao_risco IS NOT NULL` e `status_atendimento IS NULL`; seta `em_atendimento`; grava
      `Evolucao` tipo "Início de Atendimento"; 409 se fora de ordem)
- [x] 2.3 Implementar `POST /api/pacientes/{id}/atendimento/alta` (valida `status_atendimento ==
      'em_atendimento'`; seta `alta`; grava `Evolucao` tipo "Alta"; 409 se fora de ordem)
- [x] 2.4 Implementar `POST /api/pacientes/{id}/atendimento/exames` (valida `status_atendimento ==
      'em_atendimento'`; aceita `observacoes` opcional; seta `aguardando_exames`; grava `Evolucao` tipo
      "Solicitação de Exames"; 409 se fora de ordem)
- [x] 2.5 Implementar `POST /api/pacientes/{id}/atendimento/retomar` (valida `status_atendimento ==
      'aguardando_exames'`; seta `em_atendimento`; grava `Evolucao` tipo "Retomada de Atendimento"; 409 se
      fora de ordem)
- [x] 2.6 Registrar o novo router em `backend/app/api/routes/__init__.py` (ou equivalente de inclusão de
      rotas)

## 3. Painel de atendimento

- [x] 3.1 Atualizar `backend/app/schemas/painel.py` (`PainelItem`) com `pode_iniciar_atendimento`,
      `pode_dar_alta`, `pode_solicitar_exames`, `pode_retomar_atendimento`
- [x] 3.2 Atualizar `listar_painel` (`painel.py`) para derivar o status completo (5 valores) a partir de
      `classificacao_risco` + `status_atendimento`, calcular os 4 booleans por perfil/status, e excluir da
      query pacientes com `status_atendimento == 'alta'`

## 4. Specs e documentação

- [ ] 4.1 Sincronizar `openspec/specs/atendimento-medico/spec.md` (nova capability) e
      `openspec/specs/painel-atendimento/spec.md` (delta) após validação (via `openspec archive` no
      fechamento da fase)
- [x] 4.2 Atualizar `docs/03-casos-uso.md` se necessário para refletir os UCs novos (iniciar atendimento,
      alta, exames, retomar)

## 5. Testes

- [x] 5.1 Testes de transição válida para cada endpoint (iniciar, alta, exames, retomar)
- [x] 5.2 Testes de transição fora de ordem (409) para cada endpoint
- [x] 5.3 Teste de restrição de perfil (enfermeiro não pode acionar nenhuma transição)
- [x] 5.4 Teste de painel: paciente com alta não aparece na listagem; booleans de ação corretos por
      status/perfil
- [x] 5.5 Rodar suíte completa do backend e confirmar que os 69 testes existentes continuam passando
      (81/81 passando: 69 antigos + 12 novos em `test_atendimento.py`)
