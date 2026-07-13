## ADDED Requirements

### Requirement: Cadastro de paciente com validação de CPF e CNS
O sistema SHALL registrar um novo paciente somente quando nome (mínimo 3 caracteres), CPF (11 dígitos numéricos), CNS (15 dígitos numéricos) e data de nascimento forem informados e válidos.

#### Scenario: Cadastro válido
- **WHEN** o enfermeiro submete nome, CPF de 11 dígitos, CNS de 15 dígitos e data de nascimento
- **THEN** o sistema persiste o paciente com status "Aguardando Triagem" e cria uma evolução do tipo "Cadastro"

#### Scenario: CPF inválido
- **WHEN** o CPF informado não possui exatamente 11 dígitos numéricos
- **THEN** o sistema rejeita a submissão, exibe erro no campo CPF e não persiste o registro

#### Scenario: CNS inválido
- **WHEN** o CNS informado não possui exatamente 15 dígitos numéricos
- **THEN** o sistema rejeita a submissão, exibe erro no campo CNS e não persiste o registro
