# prontuario

## Purpose

Consulta somente-leitura do prontuário do paciente (UC002 / RF004): sinais vitais mais recentes,
linha do tempo de evolução e prescrições, com a ação de nova prescrição restrita ao perfil médico.

## Requirements

### Requirement: Consulta de prontuário somente leitura
O sistema SHALL exibir, para um paciente selecionado, os sinais vitais mais recentes, a linha do tempo de evolução em ordem cronológica decrescente e as prescrições registradas, em modo somente leitura.

#### Scenario: Paciente com histórico
- **WHEN** um usuário autenticado abre o prontuário de um paciente com evoluções registradas
- **THEN** o sistema exibe os sinais vitais mais recentes, as evoluções em ordem cronológica decrescente e as prescrições

#### Scenario: Paciente sem prescrições
- **WHEN** o paciente não possui prescrições registradas
- **THEN** o sistema exibe a mensagem "Nenhuma prescrição registrada." sem quebrar o layout

### Requirement: Ação de nova prescrição restrita ao perfil médico
O sistema SHALL exibir a ação "+ Nova Prescrição" apenas para usuários com perfil "medico".

#### Scenario: Botão visível para médico
- **WHEN** um usuário com perfil "medico" visualiza o prontuário
- **THEN** o sistema exibe a ação "+ Nova Prescrição"

#### Scenario: Botão oculto para enfermeiro
- **WHEN** um usuário com perfil "enfermeiro" visualiza o prontuário
- **THEN** o sistema não exibe a ação "+ Nova Prescrição"
