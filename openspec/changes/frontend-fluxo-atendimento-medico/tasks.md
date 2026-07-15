## 1. API client

- [x] 1.1 Adicionar em `frontend/src/api.js` os wrappers `iniciarAtendimento(token, pacienteId)`,
  `darAlta(token, pacienteId)`, `solicitarExames(token, pacienteId, observacoes?)`,
  `retomarAtendimento(token, pacienteId)`, chamando os 4 endpoints `POST /api/pacientes/{id}/atendimento/*`
  já existentes no backend.
- [x] 1.2 Garantir tratamento de erro 409 (transição fora de ordem) propagando a mensagem do backend para
  quem chamar essas funções.

## 2. Painel — ações condicionais

- [x] 2.1 `PainelScreen.jsx` passa a ler `pode_iniciar_atendimento`, `pode_dar_alta`,
  `pode_solicitar_exames`, `pode_retomar_atendimento` de cada item do painel.
- [x] 2.2 Renderizar botão "Iniciar Atendimento" quando `pode_iniciar_atendimento` for `true`, navegando
  para a tela dedicada (grupo 4).
- [x] 2.3 Renderizar botões "Dar Alta" e "Solicitar Exames Complementares" quando `pode_dar_alta` /
  `pode_solicitar_exames` forem `true`, abrindo o modal correspondente (grupo 3).
- [x] 2.4 Renderizar botão "Retomar Atendimento" quando `pode_retomar_atendimento` for `true`, abrindo
  modal de confirmação (grupo 3).
- [x] 2.5 Após qualquer ação confirmada com sucesso, recarregar a lista do painel (mesmo padrão já usado
  após confirmar triagem).
- [x] 2.6 Em caso de erro 409, exibir mensagem de erro ao usuário e recarregar o painel para refletir o
  status atual do paciente.

## 3. Modal de confirmação reutilizável

- [x] 3.1 Criar componente de modal de confirmação parametrizável (título, texto descritivo, campo opcional
  de observações, botões confirmar/cancelar) em `frontend/src/components/`.
- [x] 3.2 Usar o modal sem campo para "Dar Alta" e "Retomar Atendimento".
- [x] 3.3 Usar o modal com campo opcional `observacoes` para "Solicitar Exames Complementares".
- [x] 3.4 Revisar estilo do modal com a skill `ui-ux-pro-max` / `frontend-design`, seguindo o padrão visual
  já usado no restante do painel.

## 4. Tela dedicada de Iniciar Atendimento

- [x] 4.1 Criar `frontend/src/screens/IniciarAtendimentoScreen.jsx` seguindo o padrão de
  `TriagemScreen.jsx` (tela própria, dados do paciente, ação de confirmar chamando
  `iniciarAtendimento`, volta pro painel recarregando a lista).
- [x] 4.2 Adicionar navegação em `App.jsx` (`irPara("iniciar-atendimento", pacienteId)` ou equivalente) e
  o callback correspondente passado para `PainelScreen`.

## 5. Testes

- [x] 5.1 Testes de frontend (se houver suíte configurada) cobrindo: exibição condicional dos 4 botões por
  status/perfil, fluxo de confirmação de cada ação, tratamento de erro 409. (Sem suíte configurada no
  frontend — nada a adicionar; `npx oxlint` limpo.)
- [x] 5.2 Teste manual ponta a ponta: login como médico, percorrer o ciclo completo
  (Aguardando Atendimento → Iniciar → Em Atendimento → Solicitar Exames → Aguardando Exames → Retomar →
  Em Atendimento → Dar Alta) pelo painel. (Validado via chamadas HTTP diretas aos mesmos endpoints usados
  pelo frontend — backend/frontend não tinham ferramenta de browser automatizado disponível na sessão;
  ciclo completo, erro 409 fora de ordem e 403 de perfil restrito confirmados.)

## 6. Spec e fechamento

- [x] 6.1 Sincronizar a spec delta (`specs/painel-atendimento/spec.md` deste change) com
  `openspec/specs/painel-atendimento/spec.md` via `openspec-sync-specs`.
- [ ] 6.2 Arquivar o change após merge, seguindo o fluxo por fase já em uso no projeto (branch → skills →
  PR → sync develop).
