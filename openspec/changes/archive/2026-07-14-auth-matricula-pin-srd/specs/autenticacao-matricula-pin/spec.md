## ADDED Requirements

### Requirement: Login por matrícula e PIN
O sistema SHALL autenticar o colaborador via matrícula (6 dígitos numéricos) + PIN (4 dígitos numéricos), retornando um token JWT em caso de sucesso.

#### Scenario: Login bem-sucedido
- **WHEN** o colaborador submete matrícula e PIN válidos
- **THEN** o sistema retorna um token JWT e concede acesso conforme o perfil do colaborador

#### Scenario: Credenciais inválidas
- **WHEN** o colaborador submete matrícula ou PIN incorretos
- **THEN** o sistema retorna código 401 e não emite token

### Requirement: Armazenamento seguro do PIN
O sistema SHALL armazenar o PIN somente como hash (bcrypt/argon2), nunca em texto puro.

#### Scenario: Persistência do PIN
- **WHEN** o PIN de um colaborador é criado ou atualizado
- **THEN** o sistema persiste apenas `pin_hash`, nunca o PIN em texto puro

### Requirement: Controle de acesso por perfil (RBAC)
O sistema SHALL restringir ações com base no perfil do colaborador (`enfermeiro` | `medico`).

#### Scenario: Enfermeiro não pode prescrever
- **WHEN** um colaborador com perfil "enfermeiro" tenta submeter uma prescrição
- **THEN** o sistema nega a ação com código 403

#### Scenario: Médico pode prescrever
- **WHEN** um colaborador com perfil "medico" submete uma prescrição com os campos obrigatórios preenchidos
- **THEN** o sistema persiste a prescrição
