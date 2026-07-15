## ADDED Requirements

### Requirement: Iniciar atendimento médico
O sistema SHALL permitir que um usuário com perfil "medico" inicie o atendimento de um paciente cujo
prontuário já possui `classificacao_risco` definida e que ainda não teve atendimento iniciado, registrando
uma evolução do tipo "Início de Atendimento".

#### Scenario: Início de atendimento bem-sucedido
- **WHEN** um médico solicita iniciar atendimento para um paciente com status "Aguardando Atendimento"
- **THEN** o sistema marca o paciente como "Em Atendimento" e registra uma evolução "Início de Atendimento"
  com a matrícula do médico responsável

#### Scenario: Tentativa de iniciar atendimento fora de ordem
- **WHEN** um médico solicita iniciar atendimento para um paciente ainda "Aguardando Triagem" ou já "Em
  Atendimento"
- **THEN** o sistema rejeita a operação com erro de conflito e não altera o status do paciente

#### Scenario: Perfil não autorizado
- **WHEN** um usuário com perfil "enfermeiro" solicita iniciar atendimento
- **THEN** o sistema rejeita a operação

### Requirement: Dar alta ao paciente
O sistema SHALL permitir que um usuário com perfil "medico" dê alta a um paciente "Em Atendimento",
registrando uma evolução do tipo "Alta" e encerrando o atendimento.

#### Scenario: Alta bem-sucedida
- **WHEN** um médico solicita alta para um paciente com status "Em Atendimento"
- **THEN** o sistema marca o paciente como "Alta", registra uma evolução "Alta" com a matrícula do médico
  responsável, e o paciente deixa de aparecer na listagem ativa do painel

#### Scenario: Tentativa de alta fora de ordem
- **WHEN** um médico solicita alta para um paciente que não está "Em Atendimento"
- **THEN** o sistema rejeita a operação com erro de conflito

### Requirement: Solicitar exames complementares
O sistema SHALL permitir que um usuário com perfil "medico" solicite exames complementares para um
paciente "Em Atendimento", registrando uma evolução do tipo "Solicitação de Exames" e mantendo o paciente
visível no painel.

#### Scenario: Solicitação de exames bem-sucedida
- **WHEN** um médico solicita exames complementares para um paciente com status "Em Atendimento"
- **THEN** o sistema marca o paciente como "Aguardando Exames Complementares" e registra uma evolução
  "Solicitação de Exames" com a matrícula do médico responsável

#### Scenario: Tentativa de solicitar exames fora de ordem
- **WHEN** um médico solicita exames complementares para um paciente que não está "Em Atendimento"
- **THEN** o sistema rejeita a operação com erro de conflito

### Requirement: Retomar atendimento após exames
O sistema SHALL permitir que um usuário com perfil "medico" retome o atendimento de um paciente
"Aguardando Exames Complementares", registrando uma evolução do tipo "Retomada de Atendimento" e voltando
o paciente ao status "Em Atendimento".

#### Scenario: Retomada bem-sucedida
- **WHEN** um médico solicita retomar atendimento para um paciente com status "Aguardando Exames
  Complementares"
- **THEN** o sistema marca o paciente como "Em Atendimento" novamente e registra uma evolução "Retomada de
  Atendimento" com a matrícula do médico responsável

#### Scenario: Tentativa de retomar fora de ordem
- **WHEN** um médico solicita retomar atendimento para um paciente que não está "Aguardando Exames
  Complementares"
- **THEN** o sistema rejeita a operação com erro de conflito
