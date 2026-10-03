## 0. Pré-requisito

- [x] 0.1 Confirmar que `tela-atendimento-medico` foi implementado, mergeado e arquivado: coluna `queixa`,
  `AtendimentoScreen` e response enriquecido presentes em `develop`.

## 1. Backend — integridade do atendimento ativo

- [x] 1.1 Criar a migração `0006_prontuario_ativo_unico` com o índice único parcial
  `uq_prontuario_ativo_por_paciente` (`paciente_id` WHERE `deleted_at IS NULL AND status_atendimento IS
  DISTINCT FROM 'alta'`). O downgrade faz `drop_index`.
- [x] 1.2 Declarar o índice em `Prontuario.__table_args__` (`Index(..., unique=True,
  postgresql_where=...)`) para manter model e migração alinhados.
- [x] 1.3 Alterar `get_prontuario_ativo` (`deps.py`) para filtrar o episódio ativo. Sem episódio ativo,
  retorna 409 "Paciente não possui atendimento ativo".
- [x] 1.4 Alterar `consultar_prontuario` para usar o ativo ou o mais recente
  (`order_by(data_criacao.desc(), id.desc())`).
- [x] 1.5 Rodar a suíte existente e ajustar só os testes que dependem de operar sobre paciente com alta,
  documentando o motivo no teste.

## 2. Backend — retorno de paciente

- [x] 2.1 Criar `GET /api/pacientes?cpf=` (`ClinicoAtual`), retornando `list[PacienteBusca]` (`PacienteOut`
  + `atendimento_ativo`).
- [x] 2.2 Criar `POST /api/pacientes/{id}/atendimentos` (perfil `enfermeiro`):
  - cria o prontuário e a evolução "Cadastro" ("Retorno do paciente, aguardando triagem.");
  - `IntegrityError` ou existência de atendimento ativo retorna 409 "Paciente já possui atendimento ativo";
  - paciente inexistente retorna 404.
- [x] 2.3 Testes (`test_episodios.py`):
  - retorno após alta cria novo prontuário e o paciente reaparece no painel;
  - retorno com atendimento ativo retorna 409;
  - médico recebe 403;
  - busca por CPF encontrado e não encontrado;
  - prescrição em paciente com 2 episódios cai no ativo.

## 3. Backend — histórico

- [x] 3.1 Criar o schema `AtendimentoAnterior`: `prontuario_id`, `data_entrada`, `data_alta`,
  `classificacao_risco`, `queixa`, `sinais_vitais`, `evolucoes`, `prescricoes`.
- [x] 3.2 Criar `GET /api/pacientes/{id}/atendimentos` (`ClinicoAtual`), retornando os episódios com "Alta",
  do mais recente ao mais antigo. `data_alta` vem da evolução "Alta".
- [x] 3.3 Testes: paciente com 2 visitas encerradas devolve ordem e conteúdo corretos e não inclui o
  episódio ativo; primeira visita devolve lista vazia.

## 4. Frontend — cadastro com retorno

- [x] 4.1 Adicionar em `api.js` as funções `buscarPacientePorCpf`, `abrirNovoAtendimento` e
  `listarAtendimentosAnteriores`.
- [x] 4.2 Em `CadastroScreen.jsx`, quando o cadastro retornar 409, buscar por CPF e exibir:
  - cartão do paciente com "Abrir novo atendimento", se não houver atendimento ativo;
  - "Paciente já está em atendimento", se houver.
- [x] 4.3 Ao abrir o novo atendimento com sucesso: toast "Novo atendimento aberto." e voltar ao Painel.

## 5. Frontend — histórico no posto

- [ ] 5.1 Em `AtendimentoScreen.jsx`, carregar `listarAtendimentosAnteriores` junto com o prontuário.
- [ ] 5.2 Criar a seção "Atendimentos anteriores", com itens resumidos (datas de entrada e alta, cor e
  queixa) expansíveis para sinais vitais, evoluções e prescrições. Reaproveitar os blocos do change A.
- [ ] 5.3 Sem histórico, exibir "Primeiro atendimento do paciente nesta unidade.".
- [ ] 5.4 Seguir o padrão visual existente, usando `frontend-design` + `ui-ux-pro-max`.

## 6. Validação e docs

- [ ] 6.1 Fluxo manual:
  - cadastrar paciente, triar, atender e dar alta;
  - recadastrar o mesmo CPF e abrir novo atendimento;
  - triar e iniciar;
  - o posto mostra a visita anterior.
- [ ] 6.2 Atualizar `docs/03-casos-uso.md` (retorno de paciente e consulta de histórico) e
  `docs/04-modelo-dados.md` (prontuário = episódio, índice de unicidade do ativo).
