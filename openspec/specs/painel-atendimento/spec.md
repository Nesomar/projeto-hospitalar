# painel-atendimento

## Purpose

Painel de atendimento (UC006 / RF006): fila de pacientes priorizada pela classificação de risco,
com filtro por cor e a ação de triagem restrita a enfermeiros e pacientes aguardando triagem.

## Requirements

### Requirement: Listagem priorizada por classificação de risco
O sistema SHALL ordenar a lista de pacientes no painel da classificação mais grave (Vermelho) para a menos grave (Azul), com pacientes não classificados ao final, e permitir filtro por cor.

#### Scenario: Ordenação por gravidade
- **WHEN** o painel é carregado com pacientes de classificações distintas
- **THEN** o sistema ordena a lista da mais grave (Vermelho) para a menos grave (Azul)

#### Scenario: Filtro por cor
- **WHEN** o usuário seleciona o filtro de uma cor específica
- **THEN** o sistema exibe apenas pacientes daquela classificação

### Requirement: Ação de triagem restrita a enfermeiro e paciente aguardando triagem
O sistema SHALL exibir a ação "Fazer Triagem" apenas quando o paciente estiver com status "Aguardando Triagem" e o usuário tiver perfil "enfermeiro".

#### Scenario: Botão de triagem visível
- **WHEN** o paciente possui status "Aguardando Triagem" e o usuário tem perfil "enfermeiro"
- **THEN** o sistema exibe a ação "Fazer Triagem" na linha do paciente

#### Scenario: Botão de triagem oculto
- **WHEN** o paciente já possui classificação de risco ou o usuário tem perfil "medico"
- **THEN** o sistema não exibe a ação "Fazer Triagem" na linha do paciente

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
