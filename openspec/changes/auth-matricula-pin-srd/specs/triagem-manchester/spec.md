## ADDED Requirements

### Requirement: Cálculo de classificação de risco pelo Protocolo de Manchester
O sistema SHALL calcular a classificação de risco do paciente a partir dos sinais vitais informados (PA, FC, FR, Temperatura, SpO2, dor), avaliando os critérios em cascata da cor mais grave para a mais leve; o primeiro critério satisfeito define a cor.

#### Scenario: Classificação Vermelha
- **WHEN** SpO2 < 90% OU FC > 150 bpm OU PA sistólica < 80 mmHg OU dor ≥ 9
- **THEN** o sistema classifica o paciente como "Vermelho", com meta de atendimento imediato

#### Scenario: Classificação Laranja
- **WHEN** nenhum critério de Vermelho é atendido e (SpO2 < 94% OU FC > 120 bpm OU Temperatura ≥ 39,5°C OU dor ≥ 7)
- **THEN** o sistema classifica o paciente como "Laranja", com meta de atendimento em até 10 minutos

#### Scenario: Classificação Amarela
- **WHEN** nenhum critério de Vermelho ou Laranja é atendido e (SpO2 < 96% OU FC > 100 bpm OU Temperatura ≥ 38°C OU dor ≥ 4)
- **THEN** o sistema classifica o paciente como "Amarelo", com meta de atendimento em até 60 minutos

#### Scenario: Classificação Verde
- **WHEN** nenhum critério de Vermelho, Laranja ou Amarelo é atendido e (dor ≥ 1 OU FC > 90 bpm)
- **THEN** o sistema classifica o paciente como "Verde", com meta de atendimento em até 120 minutos

#### Scenario: Classificação Azul
- **WHEN** nenhum sinal vital atende aos critérios de Vermelho, Laranja, Amarelo ou Verde
- **THEN** o sistema classifica o paciente como "Azul", com meta de atendimento em até 240 minutos

### Requirement: Campos obrigatórios para calcular a classificação
O sistema SHALL exigir PA, FC, Temperatura e SpO2 preenchidos antes de permitir o cálculo da classificação de risco.

#### Scenario: Campos incompletos
- **WHEN** PA, FC, Temperatura ou SpO2 não estão preenchidos
- **THEN** o sistema bloqueia o cálculo e exibe mensagem solicitando o preenchimento dos sinais vitais

### Requirement: Confirmação da triagem
O sistema SHALL persistir a classificação de risco confirmada pelo enfermeiro e atualizar o status do paciente.

#### Scenario: Confirmação bem-sucedida
- **WHEN** o enfermeiro confirma uma classificação de risco calculada
- **THEN** o sistema persiste `classificacao_risco` no prontuário, muda o status do paciente para "Aguardando Atendimento" e cria uma evolução do tipo "Triagem"
