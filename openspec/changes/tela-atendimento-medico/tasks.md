## 1. Backend — queixa da triagem

- [x] 1.1 Adicionar coluna `queixa = Column(Text, nullable=True)` em `app/models/prontuario.py`.
- [x] 1.2 Criar migração `backend/alembic/versions/0005_prontuario_queixa.py`: `add_column` no upgrade e
  `drop_column` no downgrade.
- [x] 1.3 Em `confirmar_triagem` (`app/api/routes/triagem.py`), gravar `prontuario.queixa = payload.queixa`.
  A evolução continua como está.
- [x] 1.4 Testes em `test_triagem.py`: triagem com queixa persiste o campo; triagem sem queixa mantém o
  campo nulo e a evolução registra "sem queixa registrada".

## 2. Backend — regra de ações médicas compartilhada

- [x] 2.1 Criar `acoes_medicas(perfil: str, status: str) -> dict[str, bool]` em `app/models/prontuario.py`,
  retornando `pode_iniciar_atendimento`, `pode_dar_alta`, `pode_solicitar_exames` e
  `pode_retomar_atendimento`.
- [x] 2.2 Fazer `listar_painel` (`app/api/routes/painel.py`) usar o helper.
- [x] 2.3 Rodar `test_painel.py` e `test_atendimento.py` sem alterações: ambos devem continuar verdes.

## 3. Backend — prontuário enriquecido

- [x] 3.1 Em `app/schemas/prontuario.py`:
  - adicionar `PacienteResumo` (`data_nascimento`, `sexo`, `cpf`, `cns`, `telefone`);
  - estender `ProntuarioResponse` com `paciente: PacienteResumo`, `queixa: str | None`, `status: str` e as
    4 flags `pode_*`.
- [x] 3.2 Preencher os campos novos em `consultar_prontuario`, usando `status_efetivo` e `acoes_medicas`.
- [x] 3.3 Testes em `test_prontuario.py`:
  - médico com paciente "Em Atendimento" recebe as flags corretas e os dados do paciente;
  - enfermeiro recebe todas as flags falsas;
  - prontuário sem queixa retorna `queixa` nula.

## 4. Frontend — peças compartilhadas

- [x] 4.1 Mover `ACAO_CONFIG` de `PainelScreen.jsx` para `frontend/src/acoesAtendimento.js` e adicionar a
  entrada `iniciar` (sem observações, chama `iniciarAtendimento`). O `PainelScreen` passa a importar o
  módulo, sem mudança de comportamento.
- [x] 4.2 Extrair de `PrescricaoScreen.jsx` o componente `components/PrescricaoForm.jsx`, com campos,
  validação "Informe medicamento e dosagem." e submit via `prescrever()`. A `PrescricaoScreen` passa a
  usá-lo, sem mudança de comportamento.

## 5. Frontend — posto de atendimento

- [x] 5.1 Renomear `IniciarAtendimentoScreen.jsx` para `AtendimentoScreen.jsx` e atualizar o import e as
  props em `App.jsx`: `onAlta={voltarAoPainel}` e `onVoltar` (desseleciona o paciente).
- [x] 5.2 Na lista de seleção, filtrar itens do painel com qualquer flag `pode_*` médica verdadeira e
  exibir cor e status. Mensagem para lista vazia: "Nenhum paciente aguardando atendimento médico.".
- [x] 5.3 Criar o cabeçalho com:
  - nome, idade calculada de `data_nascimento`, sexo, CPF, CNS e telefone;
  - badge de cor e status;
  - "—" para campos ausentes.
- [x] 5.4 Criar o bloco de triagem: queixa + grade de sinais vitais (PA sistólica/diastólica, FC, FR, Temp,
  SpO2, dor).
- [x] 5.5 Criar o bloco de prescrições, com "Nenhuma prescrição registrada." para lista vazia, e a timeline
  de evoluções com data/hora e matrícula, em ordem decrescente.
- [x] 5.6 Criar a barra de ações dirigida pelas flags `pode_*`:
  - Iniciar, Exames, Alta e Retomar via `ConfirmModal` + `acoesAtendimento.js`;
  - Prescrever via modal com `PrescricaoForm`.
- [x] 5.7 Pós-sucesso das ações:
  - alta: toast e `onAlta()`;
  - demais ações: toast e recarregar o prontuário.
  - Em caso de erro: toast com a mensagem e recarregar.
- [x] 5.8 Seguir o padrão visual existente (oklch, `ACENTO`, `COLORS`), usando `frontend-design` +
  `ui-ux-pro-max`. Layout em duas colunas (triagem | ações) que empilha em telas estreitas.

## 6. Validação

- [ ] 6.1 Rodar `docker compose up`, aplicar a migração e executar a suíte do backend (verde).
- [ ] 6.2 Fluxo manual como médico:
  - Painel → Iniciar abre o posto;
  - confirmar mantém na tela com status "Em Atendimento";
  - prescrever mostra a prescrição e a evolução;
  - exames → retomar → alta volta ao Painel.
- [ ] 6.3 Regressão manual: ações do Painel (alta, exames, retomar), tela de Prescrição e Prontuário do
  enfermeiro funcionam como antes.
- [ ] 6.4 Atualizar `docs/03-casos-uso.md` (UC007) para descrever o posto de atendimento.
