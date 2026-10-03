## ADDED Requirements

### Requirement: Prontuário consultado é o atendimento atual
A consulta de prontuário do paciente SHALL retornar o atendimento ativo, ou o mais recente quando nenhum
estiver ativo. Atendimentos anteriores não aparecem misturados na linha do tempo do atendimento atual.

#### Scenario: Paciente em segundo atendimento
- **WHEN** um usuário consulta o prontuário de paciente que tem um atendimento com "Alta" e um ativo
- **THEN** o sistema retorna sinais vitais, evoluções e prescrições apenas do atendimento ativo

#### Scenario: Paciente sem atendimento ativo
- **WHEN** todos os atendimentos do paciente estão com "Alta"
- **THEN** o sistema retorna o atendimento mais recente, com status "Alta"
