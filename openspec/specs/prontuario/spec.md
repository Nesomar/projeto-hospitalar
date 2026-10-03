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

### Requirement: Prontuário inclui dados do paciente, queixa, status e ações médicas
A consulta de prontuário SHALL retornar, além dos sinais vitais, evoluções e prescrições: dados cadastrais
do paciente (data de nascimento, sexo, CPF, CNS, telefone), a queixa registrada na triagem, o status efetivo
do atendimento e as flags `pode_iniciar_atendimento`, `pode_dar_alta`, `pode_solicitar_exames` e
`pode_retomar_atendimento`, calculadas com a mesma regra usada no painel (perfil "medico" + status).

#### Scenario: Médico consulta paciente em atendimento
- **WHEN** um médico consulta o prontuário de paciente "Em Atendimento"
- **THEN** a resposta inclui os dados cadastrais, a queixa, status "Em Atendimento", `pode_dar_alta` e
  `pode_solicitar_exames` verdadeiros e `pode_iniciar_atendimento` e `pode_retomar_atendimento` falsos

#### Scenario: Enfermeiro consulta prontuário
- **WHEN** um enfermeiro consulta o prontuário de qualquer paciente
- **THEN** a resposta inclui os dados cadastrais, a queixa e o status, com todas as flags de ação médica
  falsas

#### Scenario: Paciente triado antes da coluna de queixa
- **WHEN** o prontuário foi triado antes da existência do campo de queixa
- **THEN** a resposta retorna `queixa` nula sem erro

