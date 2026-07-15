## ADDED Requirements

### Requirement: Ações de atendimento restritas a médico conforme status do paciente
O sistema SHALL exibir no painel, para cada paciente, quais ações de atendimento ("Iniciar Atendimento",
"Dar Alta", "Solicitar Exames Complementares", "Retomar Atendimento") estão disponíveis, restritas ao
perfil "medico" e ao status atual do paciente.

#### Scenario: Ação de iniciar atendimento visível
- **WHEN** o paciente possui status "Aguardando Atendimento" e o usuário tem perfil "medico"
- **THEN** o sistema exibe a ação "Iniciar Atendimento" na linha do paciente

#### Scenario: Ações de alta e exames visíveis
- **WHEN** o paciente possui status "Em Atendimento" e o usuário tem perfil "medico"
- **THEN** o sistema exibe as ações "Dar Alta" e "Solicitar Exames Complementares" na linha do paciente

#### Scenario: Ação de retomar atendimento visível
- **WHEN** o paciente possui status "Aguardando Exames Complementares" e o usuário tem perfil "medico"
- **THEN** o sistema exibe a ação "Retomar Atendimento" na linha do paciente

#### Scenario: Ações ocultas para enfermeiro
- **WHEN** o usuário tem perfil "enfermeiro"
- **THEN** o sistema não exibe nenhuma ação de iniciar atendimento, dar alta, solicitar exames ou retomar
  atendimento

### Requirement: Paciente com alta não aparece na listagem ativa
O sistema SHALL excluir da listagem do painel qualquer paciente cujo status seja "Alta".

#### Scenario: Paciente com alta excluído do painel
- **WHEN** o painel é carregado e existe paciente com status "Alta"
- **THEN** o sistema não inclui esse paciente na lista retornada
