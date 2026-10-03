## 1. Backend

- [x] 1.1 Criar o schema `DadosCadastraisRetorno` em `schemas/paciente.py` (`telefone: str | None`,
  `sexo` com padrão `^[FMO]$`, ambos opcionais) e o corpo `NovoAtendimentoIn` com `dados_cadastrais`
  opcional.
- [x] 1.2 Em `abrir_novo_atendimento`, aceitar o corpo opcional, aplicar só os campos que mudaram no
  paciente, na mesma transação do prontuário, e acrescentar "Dados atualizados: <campos>." à descrição da
  evolução "Cadastro". Validação e conflito (404/409) continuam antes de alterar o paciente.
- [x] 1.3 Testes em `test_episodios.py`:
  - telefone novo atualiza o paciente e aparece na descrição da evolução;
  - valores iguais ou corpo ausente não alteram o paciente nem a descrição;
  - sexo inválido retorna 422 e não cria atendimento;
  - atendimento ativo retorna 409 e não altera o paciente;
  - médico recebe 403.

## 2. Frontend

- [x] 2.1 Em `api.js`, `abrirNovoAtendimento(token, pacienteId, dadosCadastrais)` envia o corpo quando
  informado.
- [x] 2.2 Em `CadastroScreen.jsx`, o cartão de retorno (sem atendimento ativo) exibe telefone e sexo
  preenchidos com os valores atuais, e "Abrir novo atendimento" envia os valores do formulário.
- [x] 2.3 Seguir o padrão visual existente (`s.input`, `s.field`, `s.label`), usando `frontend-design` +
  `ui-ux-pro-max`.

## 3. Validação e docs

- [ ] 3.1 Fluxo manual: paciente com alta, recadastrar o CPF, alterar o telefone, abrir novo atendimento e
  conferir telefone atualizado e evolução "Cadastro" com "Dados atualizados: telefone.".
- [ ] 3.2 Atualizar UC004 em `docs/03-casos-uso.md` (revisão de telefone e sexo no retorno).
