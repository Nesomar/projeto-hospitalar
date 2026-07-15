## Context

`docs/03-casos-uso.md` (linha 87-94) já documenta o diagrama de estado alvo:

```
[*] --> AguardandoTriagem: Cadastro (UC004)
AguardandoTriagem --> AguardandoAtendimento: Triagem confirmada (UC001)
AguardandoAtendimento --> EmAtendimento: Atendimento médico iniciado
EmAtendimento --> [*]
```

O backend nunca implementou a metade final. Hoje (`backend/app/api/routes/painel.py:32`) o `status` do
painel é 100% derivado de `Prontuario.classificacao_risco` (NULL/não-NULL → dois estados só). Não existe
nenhuma coluna de estado, nenhum endpoint de transição, e o protótipo HTML (`docs/prototipo`) só tem o
status `'Em Atendimento'` como dado mockado estático — não define comportamento de transição, só confirma
o nome do estado.

Em conversa de exploração com o usuário, o escopo foi ampliado além do UC original para incluir dois
desfechos pós-atendimento que fazem parte do fluxo real de pronto-socorro: alta e solicitação de exames
complementares (com possibilidade de retomar o atendimento depois).

## Goals / Non-Goals

**Goals:**
- Persistir o estado de atendimento de forma auditável (quem, quando, qual transição).
- Reaproveitar o padrão já existente (`Evolucao` registrando cada evento, `responsavel_matricula`
  obrigatório, restrição por perfil via `require_perfil`/`MedicoAtual`).
- Manter os dois estados já derivados (`Aguardando Triagem`, `Aguardando Atendimento`) sem quebrar o
  painel atual — não persistir o que já é derivável de graça.
- Expor no painel quais ações cada paciente tem disponíveis, do jeito que `pode_fazer_triagem` já faz.

**Non-Goals:**
- Não modelar "exame complementar" como entidade estruturada (pedido, resultado, tipo de exame). Fica
  registrado como texto livre na `Evolucao`, igual a prescrição hoje.
- Não implementar nenhum estado pós-Alta (arquivamento, faturamento, reabertura de atendimento antigo).
- Não mexer em RNF001/RNF002 (criptografia, auditoria de leitura) — fora de escopo desta change.

## Decisions

### Uma única coluna nova, nullable, em vez de duplicar os estados já derivados

`Prontuario` ganha `status_atendimento` (enum nullable): `em_atendimento | aguardando_exames | alta`.
Quando `NULL`, o status efetivo continua derivado como hoje:
- `classificacao_risco IS NULL` → `Aguardando Triagem`
- `classificacao_risco IS NOT NULL` → `Aguardando Atendimento`

Quando `status_atendimento` está preenchido, ele manda:
- `em_atendimento` → `Em Atendimento`
- `aguardando_exames` → `Aguardando Exames Complementares`
- `alta` → `Alta` (excluído da listagem ativa do painel)

**Alternativa considerada e descartada**: enum único cobrindo os 5 estados (incluindo os dois já
derivados). Rejeitada porque exigiria escrever a coluna em `pacientes.py` (cadastro) e `triagem.py`
(confirmação) só para manter em sincronia com `classificacao_risco` — dado redundante, mais uma fonte de
verdade pra divergir. A coluna nullable evita isso: só é escrita nas transições novas.

### Transições como rota dedicada, não como parte de `prescricao.py`

Novo router `backend/app/api/routes/atendimento.py` com 4 endpoints, todos `MedicoAtual`
(`require_perfil("medico")`, mesmo padrão de `prescricao.py`):

- `POST /api/pacientes/{id}/atendimento/iniciar` — exige `classificacao_risco IS NOT NULL` e
  `status_atendimento IS NULL`; seta `em_atendimento`.
- `POST /api/pacientes/{id}/atendimento/alta` — exige `status_atendimento == 'em_atendimento'`; seta
  `alta`.
- `POST /api/pacientes/{id}/atendimento/exames` — exige `status_atendimento == 'em_atendimento'`; seta
  `aguardando_exames`. Aceita `observacoes: str` opcional pro texto da evolução.
- `POST /api/pacientes/{id}/atendimento/retomar` — exige `status_atendimento == 'aguardando_exames'`;
  volta pra `em_atendimento`.

Toda transição fora de ordem retorna `409 Conflict`, igual ao padrão já usado em
`triagem.py:41-42` ("Paciente já triado"). Cada uma grava uma `Evolucao` com `tipo` correspondente
(`"Início de Atendimento"`, `"Alta"`, `"Solicitação de Exames"`, `"Retomada de Atendimento"`).

**Alternativa considerada e descartada**: derivar `Em Atendimento` implicitamente da primeira
`Evolucao`/`Prescricao` do médico (sem endpoint dedicado). Descartada porque diverge do UC (que trata
"atendimento médico iniciado" como evento próprio) e não dá como o médico dar alta ou pedir exame sem
prescrever nada.

### Painel: `PainelItem` ganha campos de ação, não um enum de "próxima ação"

Seguindo o padrão de `pode_fazer_triagem`, adiciona 4 booleans (`pode_iniciar_atendimento`,
`pode_dar_alta`, `pode_solicitar_exames`, `pode_retomar_atendimento`), cada um calculado a partir de
`colaborador.perfil == "medico"` + status atual do paciente. Pacientes com `status_atendimento == 'alta'`
são excluídos da query do painel (`listar_painel`), não apenas escondidos no client.

## Risks / Trade-offs

- [Enum novo em coluna versus tabela de histórico de status] → Mitigação: a `Evolucao` já funciona como
  histórico (cada transição vira uma linha), não precisa de tabela extra só pra auditoria de status.
- [Corrida entre dois médicos clicando ação ao mesmo tempo] → Mitigação: mesma proteção que já existe em
  `triagem.py` (checa estado atual antes de escrever, 409 se já mudou) — sem lock adicional, aceitável no
  volume de um posto de triagem.
- [Migration Alembic em coluna de tabela já populada] → Mitigação: coluna nullable, sem backfill
  necessário (registros existentes ficam `NULL`, comportamento idêntico ao atual).

## Migration Plan

1. Migration Alembic: `ALTER TABLE prontuarios ADD COLUMN status_atendimento <enum> NULL`.
2. Deploy do backend com os 4 endpoints novos + painel atualizado.
3. Sem passo de rollback especial: `DROP COLUMN` reverte limpo (nenhum outro dado depende dela).

## Open Questions

- Nenhuma pendente — decisões de escopo (retomar exames, alta some do painel) já fechadas com o usuário
  na fase de exploração.
