## MODIFIED Requirements

### Requirement: Retorno de paciente já cadastrado
Quando o CPF informado no cadastro já pertence a um paciente, o sistema SHALL exibir os dados desse paciente
e, se ele não possuir atendimento ativo, oferecer a ação "Abrir novo atendimento" em vez de criar novo
cadastro. Antes de abrir o atendimento, o sistema SHALL permitir ao enfermeiro revisar telefone e sexo do
paciente, exibidos preenchidos com os valores atuais. Nome, data de nascimento, CPF e CNS não são editáveis
nesse fluxo.

#### Scenario: CPF de paciente com alta
- **WHEN** o enfermeiro informa no cadastro o CPF de um paciente cujo atendimento anterior está com "Alta"
- **THEN** o sistema exibe nome e data de nascimento do paciente, os campos telefone e sexo preenchidos com os
  valores atuais e a ação "Abrir novo atendimento"; ao confirmar, o paciente aparece no painel como
  "Aguardando Triagem"

#### Scenario: Telefone atualizado no retorno
- **WHEN** o enfermeiro altera o telefone no cartão de retorno e confirma "Abrir novo atendimento"
- **THEN** o sistema grava o novo telefone no paciente, abre o novo atendimento e exibe "Novo atendimento
  aberto."

#### Scenario: CPF de paciente em atendimento
- **WHEN** o enfermeiro informa o CPF de um paciente que já possui atendimento ativo
- **THEN** o sistema informa "Paciente já está em atendimento", não oferece abertura de novo atendimento e
  não permite editar os dados cadastrais
