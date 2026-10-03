## MODIFIED Requirements

### Requirement: Confirmação da triagem
O sistema SHALL persistir a classificação de risco confirmada pelo enfermeiro, os sinais vitais e a queixa principal informada (quando houver) no prontuário, e atualizar o status do paciente.

#### Scenario: Confirmação bem-sucedida
- **WHEN** o enfermeiro confirma uma classificação de risco calculada
- **THEN** o sistema persiste `classificacao_risco` no prontuário, muda o status do paciente para "Aguardando Atendimento" e cria uma evolução do tipo "Triagem"

#### Scenario: Queixa persistida no prontuário
- **WHEN** o enfermeiro confirma a triagem informando a queixa principal
- **THEN** o sistema grava a queixa no campo `queixa` do prontuário, além de citá-la na descrição da evolução "Triagem"

#### Scenario: Triagem sem queixa
- **WHEN** o enfermeiro confirma a triagem sem informar queixa
- **THEN** o sistema mantém `queixa` nula no prontuário e registra "sem queixa registrada" na evolução
