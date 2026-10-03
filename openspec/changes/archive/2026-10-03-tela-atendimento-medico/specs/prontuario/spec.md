## ADDED Requirements

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
