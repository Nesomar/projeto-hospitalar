## Why

Um paciente que já recebeu alta e volta à UPA não consegue ser atendido de novo. O recadastro falha com 409,
porque CPF e CNS são únicos, e o prontuário existente está em "Alta", um estado terminal. Por isso também não
existe histórico de visitas anteriores para o médico consultar.

O modelo de dados documentado (`docs/04-modelo-dados.md`) já prevê `PACIENTE 1:N PRONTUARIO`. O código é que
assume um único prontuário por paciente (`.first()`).

## What Changes

- Cada `PRONTUARIO` passa a representar **um atendimento (episódio)** do paciente. Paciente recorrente
  recebe um novo prontuário, e os anteriores ficam como histórico.
- Regra de integridade: no máximo **um atendimento ativo** (status diferente de "Alta" e não deletado) por
  paciente. A regra é garantida por índice único parcial no PostgreSQL.
- Novo endpoint `GET /api/pacientes?cpf=` para localizar paciente já cadastrado.
- Novo endpoint `POST /api/pacientes/{id}/atendimentos` para abrir um novo atendimento ("Aguardando
  Triagem") para paciente existente sem atendimento ativo. Registra a evolução "Cadastro" com a descrição
  "Retorno do paciente, aguardando triagem.".
- Novo endpoint `GET /api/pacientes/{id}/atendimentos` para listar os atendimentos encerrados do paciente
  (data de entrada, data da alta, classificação, queixa, evoluções e prescrições), do mais recente ao mais
  antigo.
- `get_prontuario_ativo` (todas as transições, triagem e prescrição) e `GET /prontuario` passam a operar
  sobre o atendimento **ativo**, ou o mais recente quando não há ativo, em vez de `.first()`.
- Cadastro de paciente: quando o CPF já está cadastrado, a tela oferece "Abrir novo atendimento" para o
  paciente existente, em vez de só exibir o erro.
- Posto de atendimento do médico (change `tela-atendimento-medico`): nova seção "Atendimentos anteriores"
  com a lista de visitas passadas, expansível para ver evoluções e prescrições.

## Capabilities

### New Capabilities
- `episodios-atendimento`: atendimento como episódio. Cobre unicidade do atendimento ativo, abertura de
  novo atendimento para paciente existente, busca por CPF e listagem de atendimentos anteriores.

### Modified Capabilities
- `cadastro-paciente`: CPF já cadastrado passa a oferecer a abertura de novo atendimento.
- `prontuario`: a consulta passa a se referir ao atendimento ativo, ou ao mais recente.
- `posto-atendimento-medico`: exibe o histórico de atendimentos anteriores. Depende do change
  `tela-atendimento-medico` já arquivado.

## Impact

- **Dependência**: implementar e arquivar `tela-atendimento-medico` antes. B reaproveita a coluna `queixa`
  e o posto de atendimento.
- **Backend**:
  - nova migração `0006_prontuario_ativo_unico`, com índice parcial;
  - `app/api/deps.py` (`get_prontuario_ativo`) e `app/api/routes/prontuario.py`;
  - `app/api/routes/pacientes.py` (busca por CPF, novo atendimento e histórico);
  - novos schemas.
- **Frontend**: `CadastroScreen.jsx` (fluxo de retorno), `AtendimentoScreen.jsx` (seção de histórico) e
  `api.js`.
- **Dados**: sem migração de dados. Cada paciente existente tem exatamente 1 prontuário e continua válido.
- **Painel**: sem mudança de código. O join já é por prontuário, e prontuários com alta já são filtrados.
- **Testes**: novos `test_episodios.py`; ajustes em `test_pacientes.py`.
