## Context

O backend do change `fluxo-atendimento-medico` (arquivado) já expõe:

- `GET /api/painel` retornando, por paciente, os booleans `pode_fazer_triagem`, `pode_iniciar_atendimento`,
  `pode_dar_alta`, `pode_solicitar_exames`, `pode_retomar_atendimento` (`backend/app/schemas/painel.py`,
  lógica em `backend/app/api/routes/painel.py:33-52`).
- `POST /api/pacientes/{id}/atendimento/iniciar` — sem body.
- `POST /api/pacientes/{id}/atendimento/alta` — sem body.
- `POST /api/pacientes/{id}/atendimento/exames` — body `{ observacoes?: string }`.
- `POST /api/pacientes/{id}/atendimento/retomar` — sem body.

Todos os 4 endpoints usam o helper `_transicionar` (`backend/app/api/routes/atendimento.py:16-42`), que
valida o status de origem e responde 409 se a transição estiver fora de ordem (outro colaborador já
mudou o status do paciente).

O frontend (`frontend/src/`) não tem router — `App.jsx` controla a tela ativa via state `screen` e passa
callbacks de navegação entre telas. `PainelScreen.jsx` já resolve o caso análogo de triagem: botão
condicional por boolean do painel → navega para `TriagemScreen.jsx` → confirma → volta e recarrega painel.
Esse é o padrão de referência para "Iniciar Atendimento".

## Goals / Non-Goals

**Goals:**
- Médico consegue, a partir do painel, iniciar atendimento, dar alta, solicitar exames complementares e
  retomar atendimento — mesmo nível de acesso pelo painel que a enfermeira já tem para triagem.
- Reaproveitar os padrões já existentes no frontend (card condicional, recarregar painel após ação,
  tratamento de erro) em vez de introduzir um padrão novo.
- Cobrir o caso de corrida (409) de forma visível ao usuário, já que múltiplos colaboradores podem
  interagir com o mesmo paciente entre o carregamento do painel e o clique na ação.

**Non-Goals:**
- Nenhuma mudança no backend — endpoints e schema do painel já estão prontos e testados.
- Não introduzir um router (ex. react-router) — segue o padrão de navegação por state já usado em todo
  `App.jsx`.
- Não cobrir aqui o conteúdo clínico da tela de atendimento em si (ex. campos de evolução) além do
  necessário para confirmar a transição de estado — isso é escopo de um change futuro se necessário.

## Decisions

**1. "Iniciar Atendimento" navega para tela dedicada, não ação direta no card.**
Mesmo o endpoint não exigindo body, iniciar atendimento é o ponto de entrada do médico no caso — decisão
tomada com o usuário de manter paridade com o padrão de Triagem (tela própria com confirmação), em vez de
um POST silencioso no card. Alternativa considerada: ação direta no card (mais rápida, menos cliques) —
descartada por ser a ação mais "pesada" das quatro e se beneficiar de uma tela com mais contexto do
paciente antes de confirmar.

**2. "Dar Alta" e "Retomar Atendimento" usam modal de confirmação simples; "Solicitar Exames" usa modal
com campo de observações.**
As três ações têm endpoint sem campos obrigatórios, mas são ações que mudam o estado clínico do paciente —
um clique acidental no card não deve disparar a transição sem confirmação. Um modal leve (sem navegação)
é suficiente porque não há dado complexo a coletar, exceto o campo opcional de `observacoes` em exames.

**3. Novo componente de modal reutilizável em vez de duplicar 3 modais.**
`PainelScreen.jsx` ganha um único componente de modal de confirmação parametrizável (título, texto,
campo opcional de observações, callback de confirmação), evitando duplicar JSX para alta/exames/retomar.

**4. Erro 409 tratado com mensagem + reload do painel, sem lógica de retry automático.**
Se a transição falhar por estar fora de ordem, o sistema mostra a mensagem de erro retornada pelo backend
e recarrega a lista do painel para refletir o status real — o usuário decide a próxima ação manualmente.

## Risks / Trade-offs

- [Modal genérico mal parametrizado gera UX inconsistente entre as 3 ações] → Mitigação: revisar com
  `ui-ux-pro-max` antes de finalizar o componente, seguindo o padrão de modais já usado em outras telas do
  projeto, se existir; caso contrário, manter o modal o mais simples possível (título + descrição + campo
  opcional + 2 botões).
- [Tela dedicada de "Iniciar Atendimento" adiciona um passo a mais de navegação em relação às outras 3
  ações que ficam em modal] → Aceito conscientemente: decisão do usuário priorizando consistência com
  Triagem sobre uniformidade entre as 4 ações.
- [Condição de corrida: painel carregado com `pode_dar_alta: true`, mas outro médico já deu alta antes do
  clique] → Mitigação: já coberta pelo 409 do backend; frontend só precisa expor o erro e recarregar.

## Migration Plan

Sem migração de dados. Deploy é só frontend: build e publicação do bundle React. Sem necessidade de
rollback especial — reverter o commit/PR reverte a UI para o estado atual (médico sem essas ações) sem
afetar o backend, que continua funcionando via chamadas diretas (ex. Swagger/Postman) se necessário.

## Open Questions

Nenhuma em aberto — decisões de UX (tela dedicada vs modal, onde capturar `observacoes`) já confirmadas
com o usuário durante a exploração que originou este change.
