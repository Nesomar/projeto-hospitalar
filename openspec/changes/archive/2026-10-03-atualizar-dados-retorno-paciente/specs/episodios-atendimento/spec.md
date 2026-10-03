## MODIFIED Requirements

### Requirement: Abrir novo atendimento para paciente existente
O sistema SHALL permitir que o enfermeiro abra um novo atendimento para um paciente sem atendimento ativo.
O sistema cria um novo prontuário com status "Aguardando Triagem" e registra a evolução "Cadastro" com a
descrição "Retorno do paciente, aguardando triagem." e a matrícula do responsável.

A requisição MAY incluir `dados_cadastrais` com `telefone` e `sexo`. Quando presente, o sistema SHALL
atualizar esses campos do paciente na mesma transação da abertura do atendimento. Se algum valor mudou, a
descrição da evolução "Cadastro" SHALL acrescentar os campos atualizados (ex.: "Dados atualizados:
telefone."). Se a abertura falhar, nenhum dado do paciente é alterado.

#### Scenario: Retorno de paciente com alta
- **WHEN** o enfermeiro abre novo atendimento para um paciente cujo único prontuário está com "Alta"
- **THEN** o sistema cria um novo prontuário "Aguardando Triagem", o paciente volta a aparecer no painel e o
  prontuário anterior permanece inalterado

#### Scenario: Retorno com dados cadastrais atualizados
- **WHEN** o enfermeiro abre novo atendimento informando um telefone diferente do cadastrado
- **THEN** o sistema atualiza o telefone do paciente, cria o novo prontuário e registra a evolução "Cadastro"
  com a descrição "Retorno do paciente, aguardando triagem. Dados atualizados: telefone."

#### Scenario: Retorno sem alteração de dados
- **WHEN** o enfermeiro abre novo atendimento sem `dados_cadastrais`, ou com valores iguais aos atuais
- **THEN** o sistema não altera o paciente e a evolução "Cadastro" mantém a descrição "Retorno do paciente,
  aguardando triagem."

#### Scenario: Dados cadastrais inválidos
- **WHEN** o enfermeiro informa um sexo fora de "F", "M" ou "O"
- **THEN** o sistema rejeita a requisição com erro de validação e não cria atendimento nem altera o paciente

#### Scenario: Paciente já em atendimento
- **WHEN** o enfermeiro tenta abrir novo atendimento para paciente que já possui atendimento ativo, mesmo
  informando `dados_cadastrais`
- **THEN** o sistema rejeita com erro de conflito "Paciente já possui atendimento ativo" e não altera o
  paciente

#### Scenario: Perfil médico não abre atendimento
- **WHEN** um usuário com perfil "medico" tenta abrir novo atendimento
- **THEN** o sistema rejeita a operação por falta de permissão
