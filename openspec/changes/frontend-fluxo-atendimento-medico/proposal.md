## Why

O change `fluxo-atendimento-medico` (arquivado em 2026-07-14) implementou toda a máquina de estado do
atendimento no backend — 4 endpoints de transição, os 4 booleans de ação (`pode_iniciar_atendimento`,
`pode_dar_alta`, `pode_solicitar_exames`, `pode_retomar_atendimento`) em `GET /api/painel`, e o
`Requirement: Ações de atendimento restritas a médico conforme status do paciente` já está descrito em
`openspec/specs/painel-atendimento/spec.md`. Só que o plano de tasks daquele change nunca teve uma seção de
frontend, então `PainelScreen.jsx` continua lendo só `pode_fazer_triagem`. Hoje o médico só consegue fazer
prescrição pelo prontuário — não existe nenhuma forma de iniciar atendimento, dar alta, solicitar exames ou
retomar atendimento pela interface, mesmo o backend já suportando tudo isso.

## What Changes

- Adicionar em `frontend/src/api.js` os 4 wrappers de chamada para os endpoints já existentes:
  `iniciarAtendimento`, `darAlta`, `solicitarExames` (aceita `observacoes` opcional), `retomarAtendimento`.
- `PainelScreen.jsx` passa a ler os 4 campos `pode_*` de atendimento retornados pelo painel e a exibir a
  ação correspondente na linha do paciente, restrita a perfil "medico", conforme o requirement já
  especificado.
- "Iniciar Atendimento": navega para uma tela dedicada de confirmação (mesmo padrão hoje usado por
  `TriagemScreen.jsx` a partir do painel), em vez de disparar o POST direto no card.
- "Dar Alta" e "Retomar Atendimento": ação com modal de confirmação no próprio painel (sem campos, só
  confirmar/cancelar), dado que são ações clinicamente sensíveis mesmo sem exigirem corpo na requisição.
- "Solicitar Exames Complementares": modal inline no painel com campo `observacoes` opcional antes de
  confirmar.
- Após qualquer ação bem-sucedida, o painel recarrega a lista (mesmo padrão já usado após confirmar
  triagem).
- Tratamento de erro 409 (transição fora de ordem) exibido ao usuário de forma clara, já que outro
  colaborador pode ter alterado o status do paciente entre o carregamento do painel e o clique na ação.

## Capabilities

### New Capabilities
(nenhuma)

### Modified Capabilities
- `painel-atendimento`: o requirement "Ações de atendimento restritas a médico conforme status do
  paciente" ganha cenários explícitos sobre o mecanismo de confirmação de cada ação (tela dedicada para
  iniciar atendimento, modal para dar alta/retomar/solicitar exames) e sobre o comportamento em caso de
  transição rejeitada por estar fora de ordem — detalhes de UI que ainda não estavam especificados.

## Impact

- `frontend/src/api.js` — novas funções de chamada HTTP.
- `frontend/src/screens/PainelScreen.jsx` — novos botões condicionais e dois modais (confirmação simples
  para alta/retomar, modal com campo para exames).
- Nova tela `frontend/src/screens/IniciarAtendimentoScreen.jsx` (ou nome equivalente) + roteamento em
  `App.jsx`.
- Nenhuma mudança no backend — todos os endpoints e o schema do painel já existem e estão testados.
