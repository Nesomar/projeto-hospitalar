# episodios-atendimento Specification

## Purpose
Tratar cada prontuário como um episódio de atendimento, de modo que paciente que retorna à UPA abra um novo atendimento em vez de ficar bloqueado. Garante no máximo um atendimento ativo por paciente, permite localizar paciente por CPF, abrir novo atendimento e listar os atendimentos encerrados como histórico.
## Requirements
### Requirement: Um único atendimento ativo por paciente
O sistema SHALL garantir que cada paciente tenha no máximo um prontuário ativo, ou seja, não deletado e com
status diferente de "Alta". Todas as operações de triagem, prescrição e transição de atendimento SHALL atuar
sobre esse prontuário ativo.

#### Scenario: Operação sobre o atendimento ativo
- **WHEN** um paciente possui um prontuário com "Alta" e outro ativo, e um médico prescreve para o paciente
- **THEN** a prescrição é registrada no prontuário ativo

#### Scenario: Paciente sem atendimento ativo
- **WHEN** todos os prontuários do paciente estão com "Alta" e um médico tenta iniciar atendimento,
  prescrever ou o enfermeiro tenta triar
- **THEN** o sistema rejeita a operação com erro de conflito informando que o paciente não possui atendimento
  ativo

#### Scenario: Banco impede dois atendimentos ativos
- **WHEN** duas requisições concorrentes tentam abrir atendimento para o mesmo paciente
- **THEN** apenas uma é efetivada e a outra recebe erro de conflito

### Requirement: Busca de paciente por CPF
O sistema SHALL permitir que usuários com perfil clínico ("enfermeiro" ou "medico") localizem um paciente
cadastrado pelo CPF, retornando seus dados cadastrais e se ele possui atendimento ativo.

#### Scenario: CPF encontrado
- **WHEN** o enfermeiro busca por um CPF cadastrado
- **THEN** o sistema retorna os dados do paciente e o indicador `atendimento_ativo`

#### Scenario: CPF não encontrado
- **WHEN** o enfermeiro busca por um CPF não cadastrado
- **THEN** o sistema retorna lista vazia

### Requirement: Abrir novo atendimento para paciente existente
O sistema SHALL permitir que o enfermeiro abra um novo atendimento para um paciente sem atendimento ativo.
O sistema cria um novo prontuário com status "Aguardando Triagem" e registra a evolução "Cadastro" com a
descrição "Retorno do paciente, aguardando triagem." e a matrícula do responsável.

#### Scenario: Retorno de paciente com alta
- **WHEN** o enfermeiro abre novo atendimento para um paciente cujo único prontuário está com "Alta"
- **THEN** o sistema cria um novo prontuário "Aguardando Triagem", o paciente volta a aparecer no painel e o
  prontuário anterior permanece inalterado

#### Scenario: Paciente já em atendimento
- **WHEN** o enfermeiro tenta abrir novo atendimento para paciente que já possui atendimento ativo
- **THEN** o sistema rejeita com erro de conflito "Paciente já possui atendimento ativo"

#### Scenario: Perfil médico não abre atendimento
- **WHEN** um usuário com perfil "medico" tenta abrir novo atendimento
- **THEN** o sistema rejeita a operação por falta de permissão

### Requirement: Listar atendimentos anteriores do paciente
O sistema SHALL listar, para usuários clínicos, os atendimentos encerrados ("Alta") do paciente, do mais
recente ao mais antigo. Cada item SHALL conter: data de entrada, data da alta (data da evolução "Alta"),
classificação de risco, queixa, sinais vitais, evoluções e prescrições daquele atendimento.

#### Scenario: Paciente com visitas anteriores
- **WHEN** um médico consulta os atendimentos anteriores de paciente com dois atendimentos encerrados
- **THEN** o sistema retorna os dois, do mais recente ao mais antigo, cada um com suas evoluções e
  prescrições

#### Scenario: Primeira visita
- **WHEN** o paciente não possui atendimento encerrado
- **THEN** o sistema retorna lista vazia

