# painel-atendimento

## Purpose

Painel de atendimento (UC006 / RF006): fila de pacientes priorizada pela classificação de risco,
com filtro por cor e a ação de triagem restrita a enfermeiros e pacientes aguardando triagem.

## Requirements

### Requirement: Listagem priorizada por classificação de risco
O sistema SHALL ordenar a lista de pacientes no painel da classificação mais grave (Vermelho) para a menos grave (Azul), com pacientes não classificados ao final, e permitir filtro por cor.

#### Scenario: Ordenação por gravidade
- **WHEN** o painel é carregado com pacientes de classificações distintas
- **THEN** o sistema ordena a lista da mais grave (Vermelho) para a menos grave (Azul)

#### Scenario: Filtro por cor
- **WHEN** o usuário seleciona o filtro de uma cor específica
- **THEN** o sistema exibe apenas pacientes daquela classificação

### Requirement: Ação de triagem restrita a enfermeiro e paciente aguardando triagem
O sistema SHALL exibir a ação "Fazer Triagem" apenas quando o paciente estiver com status "Aguardando Triagem" e o usuário tiver perfil "enfermeiro".

#### Scenario: Botão de triagem visível
- **WHEN** o paciente possui status "Aguardando Triagem" e o usuário tem perfil "enfermeiro"
- **THEN** o sistema exibe a ação "Fazer Triagem" na linha do paciente

#### Scenario: Botão de triagem oculto
- **WHEN** o paciente já possui classificação de risco ou o usuário tem perfil "medico"
- **THEN** o sistema não exibe a ação "Fazer Triagem" na linha do paciente
