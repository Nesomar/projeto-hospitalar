## Why

No retorno de um paciente à UPA, o cadastro só permite "Abrir novo atendimento". Se o telefone mudou, o dado
fica desatualizado e a unidade perde o contato com o paciente. O change `episodios-atendimento` deixou isso
como pendência explícita (Non-Goal e Open Question do design).

## What Changes

- No cartão de retorno (CPF já cadastrado, sem atendimento ativo), o enfermeiro pode corrigir **telefone** e
  **sexo** antes de abrir o novo atendimento. Os campos vêm preenchidos com os valores atuais.
- `POST /api/pacientes/{id}/atendimentos` passa a aceitar um corpo opcional `dados_cadastrais`
  (`telefone`, `sexo`). A atualização e a abertura do atendimento acontecem na mesma transação: ou as duas
  efetivam, ou nenhuma.
- Quando algum dado muda, a evolução "Cadastro" do novo atendimento registra o que foi atualizado
  (ex.: "Retorno do paciente, aguardando triagem. Dados atualizados: telefone."), com a matrícula do
  responsável. Isso mantém a rastreabilidade sem criar tabela de auditoria.
- Sem corpo, ou com valores iguais aos atuais, o comportamento de hoje não muda.
- **Fora de escopo**: nome, data de nascimento, CPF e CNS. São identificadores; correção deles é um fluxo
  administrativo à parte. O modelo também não tem endereço, e adicionar a coluna fica para outro change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `cadastro-paciente`: o cartão de retorno permite revisar telefone e sexo antes de abrir o atendimento.
- `episodios-atendimento`: a abertura de novo atendimento aceita atualização opcional de telefone e sexo e a
  registra na evolução "Cadastro".

## Impact

- **Backend**: `app/api/routes/pacientes.py` (`abrir_novo_atendimento`) e `app/schemas/paciente.py`
  (novo schema do corpo opcional). Sem migração.
- **Frontend**: `CadastroScreen.jsx` (campos no cartão de retorno) e `api.js` (`abrirNovoAtendimento` passa a
  enviar o corpo).
- **Testes**: casos novos em `test_episodios.py`.
- **Docs**: UC004 em `docs/03-casos-uso.md`.
- **Compatibilidade**: o corpo é opcional, então clientes atuais continuam funcionando.
