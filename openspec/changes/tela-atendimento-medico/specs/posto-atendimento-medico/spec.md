## ADDED Requirements

### Requirement: Seleção de paciente no posto de atendimento
O sistema SHALL listar na aba "Atendimento" do perfil "medico" todos os pacientes ativos com status
"Aguardando Atendimento", "Em Atendimento" ou "Aguardando Exames Complementares", ordenados por gravidade,
exibindo nome, cor de risco e status, e permitir selecionar um deles para abrir o posto de atendimento.

#### Scenario: Lista inclui pacientes em qualquer etapa médica
- **WHEN** o médico abre a aba "Atendimento" sem paciente selecionado e existem pacientes "Aguardando
  Atendimento", "Em Atendimento" e "Aguardando Exames Complementares"
- **THEN** o sistema lista os três pacientes com sua cor de risco e status

#### Scenario: Pacientes não triados ficam fora da lista
- **WHEN** existe paciente com status "Aguardando Triagem"
- **THEN** o sistema não o inclui na lista da aba "Atendimento"

#### Scenario: Nenhum paciente disponível
- **WHEN** não há paciente em etapa médica
- **THEN** o sistema exibe "Nenhum paciente aguardando atendimento médico."

### Requirement: Posto de atendimento exibe dados do paciente e da triagem
O sistema SHALL exibir, no posto de atendimento do paciente selecionado: nome, idade (calculada a partir da
data de nascimento), sexo, CPF, CNS, telefone, cor de risco, status atual, queixa principal da triagem e
sinais vitais (PA sistólica/diastólica, FC, FR, Temperatura, SpO2, dor).

#### Scenario: Paciente triado com queixa
- **WHEN** o médico abre o posto de atendimento de um paciente cuja triagem registrou queixa
- **THEN** o sistema exibe os dados cadastrais, a idade, a cor de risco, o status, a queixa e os sinais
  vitais

#### Scenario: Campo opcional ausente
- **WHEN** o paciente não possui telefone, sexo, queixa ou algum sinal vital opcional registrado
- **THEN** o sistema exibe "—" no lugar do valor ausente sem quebrar o layout

### Requirement: Posto de atendimento exibe prescrições e evoluções do atendimento atual
O sistema SHALL exibir no posto de atendimento as prescrições e a linha do tempo de evoluções do prontuário
atual, em ordem cronológica decrescente, cada item com data/hora e matrícula do responsável.

#### Scenario: Atendimento com prescrições e evoluções
- **WHEN** o prontuário possui prescrições e evoluções
- **THEN** o sistema lista ambas em ordem cronológica decrescente

#### Scenario: Atendimento sem prescrições
- **WHEN** o prontuário não possui prescrições
- **THEN** o sistema exibe "Nenhuma prescrição registrada."

### Requirement: Ações médicas contextuais no posto de atendimento
O sistema SHALL exibir no posto de atendimento apenas as ações disponíveis para o status atual do paciente,
conforme as flags retornadas pelo backend: "Iniciar Atendimento" (Aguardando Atendimento); "Prescrever",
"Solicitar Exames Complementares" e "Dar Alta" (Em Atendimento); "Retomar Atendimento" (Aguardando Exames
Complementares). "Dar Alta" e "Retomar Atendimento" SHALL exigir modal de confirmação; "Solicitar Exames
Complementares" SHALL exibir modal com campo opcional de observações; "Prescrever" SHALL exibir modal com o
formulário de prescrição (medicamento e dosagem obrigatórios; via, frequência e observações).

#### Scenario: Paciente aguardando atendimento
- **WHEN** o posto é aberto para paciente "Aguardando Atendimento"
- **THEN** o sistema exibe apenas a ação "Iniciar Atendimento"

#### Scenario: Paciente em atendimento
- **WHEN** o posto é aberto para paciente "Em Atendimento"
- **THEN** o sistema exibe as ações "Prescrever", "Solicitar Exames Complementares" e "Dar Alta"

#### Scenario: Paciente aguardando exames
- **WHEN** o posto é aberto para paciente "Aguardando Exames Complementares"
- **THEN** o sistema exibe apenas a ação "Retomar Atendimento"

#### Scenario: Prescrição pelo posto
- **WHEN** o médico preenche medicamento e dosagem no modal "Prescrever" e confirma
- **THEN** o sistema registra a prescrição, fecha o modal e recarrega o posto exibindo a nova prescrição e a
  nova evolução "Prescrição"

#### Scenario: Prescrição sem campos obrigatórios
- **WHEN** o médico confirma o modal "Prescrever" sem medicamento ou dosagem
- **THEN** o sistema não envia a requisição e exibe "Informe medicamento e dosagem."

### Requirement: Médico permanece no posto após transições
O sistema SHALL, após "Iniciar Atendimento", "Solicitar Exames Complementares", "Retomar Atendimento" ou
"Prescrever" concluídos com sucesso, manter o médico no posto de atendimento do mesmo paciente e recarregar
os dados (status, ações, prescrições, evoluções). Após "Dar Alta" concluída com sucesso, o sistema SHALL
retornar ao Painel.

#### Scenario: Iniciar atendimento mantém o médico no posto
- **WHEN** o médico confirma "Iniciar Atendimento" e o backend aceita
- **THEN** o sistema permanece no posto, exibe status "Em Atendimento" e as ações "Prescrever", "Solicitar
  Exames Complementares" e "Dar Alta"

#### Scenario: Alta retorna ao painel
- **WHEN** o médico confirma "Dar Alta" e o backend aceita
- **THEN** o sistema exibe "Alta registrada." e navega para o Painel

#### Scenario: Transição rejeitada
- **WHEN** o backend rejeita uma ação com erro de status fora de ordem
- **THEN** o sistema exibe a mensagem de erro e recarrega o posto com o status atual
