## ADDED Requirements

### Requirement: Registro de prescrição médica
O sistema SHALL registrar uma prescrição somente quando medicamento e dosagem estiverem preenchidos, vinculando-a ao paciente e ao médico responsável.

#### Scenario: Prescrição válida
- **WHEN** o médico submete medicamento e dosagem preenchidos (via, frequência e observações são opcionais)
- **THEN** o sistema persiste a prescrição vinculada ao paciente e ao médico responsável, e cria uma evolução do tipo "Prescrição"

#### Scenario: Campos obrigatórios ausentes
- **WHEN** medicamento ou dosagem não estão preenchidos
- **THEN** o sistema rejeita a submissão e exibe mensagem informando os campos obrigatórios
