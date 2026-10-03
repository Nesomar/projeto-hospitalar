## ADDED Requirements

### Requirement: Retorno de paciente já cadastrado
Quando o CPF informado no cadastro já pertence a um paciente, o sistema SHALL exibir os dados desse paciente
e, se ele não possuir atendimento ativo, oferecer a ação "Abrir novo atendimento" em vez de criar novo
cadastro.

#### Scenario: CPF de paciente com alta
- **WHEN** o enfermeiro informa no cadastro o CPF de um paciente cujo atendimento anterior está com "Alta"
- **THEN** o sistema exibe nome e data de nascimento do paciente e a ação "Abrir novo atendimento"; ao
  confirmar, o paciente aparece no painel como "Aguardando Triagem"

#### Scenario: CPF de paciente em atendimento
- **WHEN** o enfermeiro informa o CPF de um paciente que já possui atendimento ativo
- **THEN** o sistema informa "Paciente já está em atendimento" e não oferece abertura de novo atendimento
