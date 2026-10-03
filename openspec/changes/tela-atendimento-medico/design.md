## Context

`IniciarAtendimentoScreen` já chama `GET /api/pacientes/{id}/prontuario`, mas renderiza só nome e cor.
As ações médicas vivem em três lugares:
- transições no `PainelScreen`, via `ACAO_CONFIG` + `ConfirmModal`;
- prescrição no `PrescricaoScreen`;
- leitura do prontuário no `ProntuarioScreen`.

A regra "qual ação está disponível" é calculada no backend, em `painel.py`, a partir de perfil +
`status_efetivo`. A queixa da triagem só existe embutida no texto da evolução "Triagem". O modelo atual é
1 paciente = 1 prontuário; histórico entre visitas fica para o change `episodios-atendimento`.

## Goals / Non-Goals

**Goals:**
- Uma tela onde o médico vê tudo do paciente e executa todas as ações do atendimento.
- Reutilizar o que já existe: endpoint de prontuário, `ConfirmModal`, `ACAO_CONFIG`, formulário de
  prescrição e regra de flags do painel.
- Mudança de API só aditiva.

**Non-Goals:**
- Histórico de visitas anteriores (change B).
- Exames estruturados.
- Redesenho visual do Painel ou do Prontuário.
- Remover as abas "Prontuário" e "Prescrição" do médico. Continuam existindo; avaliar depois do uso real.

## Decisions

**1. Estender `GET /prontuario` em vez de criar endpoint novo.**
O posto de atendimento já consome esse endpoint. Os campos novos entram de forma aditiva:
- objeto `paciente` com `data_nascimento`, `sexo`, `cpf`, `cns` e `telefone`;
- `queixa`, `status` e as 4 flags `pode_*`.

A `ProntuarioScreen` ignora o que não usa. Alternativa considerada: `GET /atendimento/{id}` dedicado.
Rejeitada porque duplicaria as queries.

**2. Flags calculadas no backend por helper compartilhado.**
Extrair de `painel.py` a função `acoes_medicas(perfil, status) -> dict[str, bool]`, colocada em
`app/models/prontuario.py`, ao lado de `status_efetivo`. Painel e prontuário passam a usá-la. Assim a regra
fica em um lugar só e o front não reimplementa a máquina de estados. Alternativa considerada: calcular no
front a partir do `status`. Rejeitada porque duplicaria a regra que o backend já valida com 409.

**3. Coluna `prontuarios.queixa` (Text, nullable) + migração `0005`.**
A coluna é gravada em `confirmar_triagem`. Prontuários antigos não recebem backfill e ficam com `queixa`
nula; o front exibe "—". Alternativa considerada: fazer parsing do texto da evolução. Rejeitada por ser
frágil. Também não se faz backfill via parsing, porque é dado de dev e não vale o risco.

**4. Idade calculada no front.**
O backend devolve só `data_nascimento`, sem campo derivado na API. É um cálculo de uma linha.

**5. CPF exibido completo.**
Só perfis clínicos autenticados acessam o endpoint (`ClinicoAtual`), e a identificação inequívoca do
paciente é um requisito clínico. Mascaramento fica para quando houver requisito LGPD explícito.

**6. Prescrição em modal reaproveitando o formulário.**
Extrair de `PrescricaoScreen` um componente `PrescricaoForm`, com campos, validação e submit via
`prescrever()`. A `PrescricaoScreen` e o novo modal do posto passam a usá-lo. Alternativa considerada:
navegar para a aba Prescrição e voltar. Rejeitada porque é exatamente o vai-e-vem que o change quer
eliminar.

**7. Transições reaproveitam `ACAO_CONFIG` + `ConfirmModal`.**
Mover `ACAO_CONFIG` de `PainelScreen` para um módulo compartilhado (`frontend/src/acoesAtendimento.js`) e
adicionar a entrada `iniciar`, que não tem campos. Painel e posto usam o mesmo mapa. No posto, o
pós-sucesso recarrega o prontuário; para `alta`, chama `onAlta()` e volta ao Painel.

**8. Lista de seleção da aba Atendimento.**
Continua usando `GET /api/painel`. O filtro no front passa de `pode_iniciar_atendimento` para
"qualquer `pode_*` médico verdadeiro". Não precisa de endpoint novo.

**9. Navegação.**
O componente é renomeado para `AtendimentoScreen`, mantendo `screen === "atendimento"` no `App`:
- após iniciar ou executar outras ações, permanece na tela e chama `recarregar()`;
- após alta, chama `voltarAoPainel()`;
- "Voltar" (antigo "Cancelar") desseleciona o paciente e volta à lista.

## Risks / Trade-offs

- [Response do prontuário maior, com dados pessoais] → Sem mudança de controle de acesso, porque o endpoint
  já é restrito a clínicos. É o mesmo dado que o enfermeiro digitou no cadastro.
- [Mover `ACAO_CONFIG` mexe no Painel, que já funciona] → O conteúdo é movido sem mudança de comportamento.
  Validar manualmente as ações no Painel.
- [Extração do helper pode alterar as flags do painel] → `test_painel.py` existente cobre as flags e precisa
  continuar verde sem alteração.
- [Prontuários sem `queixa`] → Aceito; exibem "—".

## Migration Plan

1. Migração `0005_prontuario_queixa`: `add_column` nullable. O downgrade faz `drop_column`. É reversível e
   não há perda de dados nos outros campos.
2. Deploy do backend antes do front. O front antigo ignora os campos novos.
3. Rollback: reverter o front, depois o backend, depois rodar `alembic downgrade -1`.

## Open Questions

- As abas "Prontuário" e "Prescrição" do médico ainda são necessárias depois do posto? Decidir com o uso
  real; fora deste change.
