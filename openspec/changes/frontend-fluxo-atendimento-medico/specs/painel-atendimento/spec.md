## MODIFIED Requirements

### Requirement: Ações de atendimento restritas a médico conforme status do paciente
O sistema SHALL exibir no painel, para cada paciente, quais ações de atendimento ("Iniciar Atendimento",
"Dar Alta", "Solicitar Exames Complementares", "Retomar Atendimento") estão disponíveis, restritas ao
perfil "medico" e ao status atual do paciente. Ao acionar "Iniciar Atendimento", o sistema SHALL navegar
para uma tela dedicada de confirmação antes de efetivar a transição. Ao acionar "Dar Alta" ou "Retomar
Atendimento", o sistema SHALL exibir um modal de confirmação (sem campos) antes de efetivar a transição.
Ao acionar "Solicitar Exames Complementares", o sistema SHALL exibir um modal com campo opcional de
observações antes de efetivar a transição. Se a transição for rejeitada pelo backend por estar fora de
ordem, o sistema SHALL exibir uma mensagem de erro ao usuário e manter o paciente na listagem com seu
status atualizado.

#### Scenario: Ação de iniciar atendimento visível
- **WHEN** o paciente possui status "Aguardando Atendimento" e o usuário tem perfil "medico"
- **THEN** o sistema exibe a ação "Iniciar Atendimento" na linha do paciente

#### Scenario: Iniciar atendimento abre tela dedicada
- **WHEN** o usuário aciona "Iniciar Atendimento" na linha do paciente
- **THEN** o sistema navega para uma tela dedicada de confirmação, sem efetivar a transição antes da
  confirmação do usuário nessa tela

#### Scenario: Ações de alta e exames visíveis
- **WHEN** o paciente possui status "Em Atendimento" e o usuário tem perfil "medico"
- **THEN** o sistema exibe as ações "Dar Alta" e "Solicitar Exames Complementares" na linha do paciente

#### Scenario: Dar alta abre modal de confirmação
- **WHEN** o usuário aciona "Dar Alta" na linha do paciente
- **THEN** o sistema exibe um modal de confirmação sem campos, e só efetiva a transição após o usuário
  confirmar

#### Scenario: Solicitar exames abre modal com campo de observações
- **WHEN** o usuário aciona "Solicitar Exames Complementares" na linha do paciente
- **THEN** o sistema exibe um modal com campo opcional de observações, e só efetiva a transição após o
  usuário confirmar

#### Scenario: Ação de retomar atendimento visível
- **WHEN** o paciente possui status "Aguardando Exames Complementares" e o usuário tem perfil "medico"
- **THEN** o sistema exibe a ação "Retomar Atendimento" na linha do paciente

#### Scenario: Retomar atendimento abre modal de confirmação
- **WHEN** o usuário aciona "Retomar Atendimento" na linha do paciente
- **THEN** o sistema exibe um modal de confirmação sem campos, e só efetiva a transição após o usuário
  confirmar

#### Scenario: Ações ocultas para enfermeiro
- **WHEN** o usuário tem perfil "enfermeiro"
- **THEN** o sistema não exibe nenhuma ação de iniciar atendimento, dar alta, solicitar exames ou retomar
  atendimento

#### Scenario: Transição rejeitada por estar fora de ordem
- **WHEN** o usuário confirma uma ação de atendimento e o backend responde com erro de status fora de
  ordem
- **THEN** o sistema exibe uma mensagem de erro ao usuário e recarrega o painel para refletir o status
  atual do paciente
