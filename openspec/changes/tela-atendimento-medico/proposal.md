## Why

Na aba "Atendimento" o médico vê só o nome do paciente, a cor da triagem e o botão "Iniciar Atendimento".
As outras ações estão espalhadas por telas diferentes:
- solicitar exames, dar alta e retomar ficam só no Painel;
- prescrever fica na aba Prescrição;
- sinais vitais e evoluções ficam na aba Prontuário.

Para atender um paciente, o médico precisa navegar entre 3 ou 4 telas. Além disso, a tela de atendimento já
carrega o prontuário completo e descarta quase tudo.

## What Changes

- A aba "Atendimento" do médico vira um **posto de trabalho** do paciente selecionado. A tela mostra:
  - cabeçalho com dados do paciente (nome, idade, sexo, CPF, CNS, telefone), cor de risco e status atual;
  - bloco de triagem com queixa principal e sinais vitais (PA, FC, FR, Temp, SpO2, dor);
  - prescrições e linha do tempo de evoluções do atendimento atual;
  - ações conforme o status: Iniciar Atendimento, Prescrever, Solicitar Exames, Dar Alta e Retomar
    Atendimento.
- Depois de "Iniciar Atendimento", o médico **permanece** na tela, que recarrega com o novo status, em vez
  de voltar ao Painel.
- Prescrever passa a ser possível dentro do posto de trabalho, via modal com o mesmo formulário da tela de
  Prescrição.
- A lista de seleção da aba "Atendimento" passa a incluir todo paciente com alguma ação médica disponível
  (Aguardando Atendimento, Em Atendimento e Aguardando Exames). Antes listava só os "Aguardando
  Atendimento".
- No Painel, "Iniciar Atendimento" continua abrindo a mesma tela, agora o posto de trabalho completo.
- Backend:
  - `GET /api/pacientes/{id}/prontuario` passa a retornar os dados cadastrais do paciente, a `queixa` da
    triagem, o status efetivo e as flags `pode_iniciar_atendimento`, `pode_dar_alta`,
    `pode_solicitar_exames` e `pode_retomar_atendimento`, calculadas pela mesma regra do painel;
  - nova coluna `prontuarios.queixa` (nullable), preenchida na confirmação da triagem. A evolução "Triagem"
    continua registrando a queixa no texto.
- Fora de escopo:
  - histórico de visitas anteriores, tratado no change `episodios-atendimento`;
  - exames estruturados (continuam como texto livre em observações).

## Capabilities

### New Capabilities
- `posto-atendimento-medico`: tela unificada de atendimento do médico. Reúne dados do paciente, triagem,
  prescrições, evoluções e ações contextuais por status.

### Modified Capabilities
- `prontuario`: a consulta passa a incluir dados cadastrais do paciente, queixa da triagem, status efetivo e
  flags de ações médicas disponíveis.
- `triagem-manchester`: a confirmação da triagem passa a persistir a queixa principal em campo próprio do
  prontuário.
- `painel-atendimento`: "Iniciar Atendimento" deixa de abrir uma tela de confirmação e passa a abrir o posto
  de atendimento, onde a confirmação acontece.

## Impact

- **Backend**:
  - `app/models/prontuario.py` (coluna `queixa`);
  - nova migração `0005_prontuario_queixa`;
  - `app/api/routes/triagem.py`, `app/api/routes/prontuario.py` e `app/schemas/prontuario.py`;
  - extração da regra de ações médicas de `app/api/routes/painel.py` para um helper compartilhado.
- **Frontend**:
  - `IniciarAtendimentoScreen.jsx` é reescrita como posto de trabalho;
  - o formulário de `PrescricaoScreen.jsx` é extraído para componente reutilizável;
  - `App.jsx` muda o fluxo de navegação pós-iniciar.
- **API**: mudança só aditiva no response do prontuário, sem quebra para a `ProntuarioScreen`.
- **Testes**: `test_prontuario.py`, `test_triagem.py` e `test_painel.py` (o helper não pode mudar o
  comportamento do painel).
