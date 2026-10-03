## ADDED Requirements

### Requirement: Posto de atendimento exibe atendimentos anteriores
O posto de atendimento SHALL exibir a seção "Atendimentos anteriores" com os atendimentos encerrados do
paciente, do mais recente ao mais antigo. Cada item mostra data de entrada, data da alta, cor de risco e
queixa, e pode ser expandido para exibir sinais vitais, evoluções e prescrições daquele atendimento.

#### Scenario: Paciente com histórico
- **WHEN** o médico abre o posto de paciente com atendimentos anteriores
- **THEN** o sistema lista os atendimentos anteriores resumidos e, ao expandir um deles, exibe suas evoluções
  e prescrições

#### Scenario: Primeira visita
- **WHEN** o paciente não possui atendimentos anteriores
- **THEN** o sistema exibe "Primeiro atendimento do paciente nesta unidade."
