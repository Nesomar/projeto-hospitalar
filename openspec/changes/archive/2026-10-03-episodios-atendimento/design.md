## Context

`docs/04-modelo-dados.md` já modela `PACIENTE ||--o{ PRONTUARIO`, e a tabela `prontuarios` não tem unique
em `paciente_id`. O código, porém, trata a relação como 1:1:
- `get_prontuario_ativo` (`deps.py`) e `consultar_prontuario` fazem `.first()` sem ordenação nem filtro de
  status;
- `cadastrar_paciente` é o único ponto que cria prontuário, e CPF e CNS são `unique`;
- "Alta" é estado terminal.

Resultado: paciente que volta fica bloqueado.

Este change pressupõe `tela-atendimento-medico` arquivado, ou seja, com coluna `queixa`, `AtendimentoScreen`
e response do prontuário enriquecido já existentes.

## Goals / Non-Goals

**Goals:**
- Prontuário = episódio. Retorno de paciente abre um novo episódio.
- No máximo 1 episódio ativo por paciente, garantido pelo banco.
- Médico vê as visitas anteriores no posto de atendimento.

**Non-Goals:**
- Atualizar dados cadastrais no retorno (telefone mudou etc.). Fica para outro change.
- Busca por nome ou CNS. Só por CPF, que é o identificador já validado no cadastro.
- Unificar pacientes duplicados.
- Paginação do histórico. Volume de UPA por paciente é baixo; adicionar quando precisar.

## Decisions

**1. Reaproveitar `prontuarios` como episódio, sem tabela `atendimentos`.**
O schema já é 1:N e evoluções e prescrições já pendem do prontuário. Alternativa considerada: tabela
`atendimento` intermediária. Rejeitada porque duplica `prontuario` e exige migrar evoluções e prescrições.

**2. Índice único parcial no PostgreSQL (migração `0006`).**
```sql
CREATE UNIQUE INDEX uq_prontuario_ativo_por_paciente
  ON prontuarios (paciente_id)
  WHERE deleted_at IS NULL AND status_atendimento IS DISTINCT FROM 'alta';
```
A regra "1 ativo" fica no banco, o que fecha a corrida entre duas aberturas concorrentes. O `IntegrityError`
vira 409. Alternativa considerada: só checar no código. Rejeitada porque deixa uma janela de concorrência.
Os dados atuais (1 prontuário por paciente) já satisfazem o índice.

**3. Resolução do prontuário "atual".**
- `get_prontuario_ativo`: filtra `status_atendimento IS DISTINCT FROM 'alta'` e mantém `with_for_update()`.
  Sem resultado, devolve 409 "Paciente não possui atendimento ativo". Hoje devolve 404 "Prontuário não
  encontrado"; o 404 continua só para paciente inexistente.
- `consultar_prontuario`: retorna o ativo ou, se não houver, o mais recente
  (`order_by(data_criacao.desc(), id.desc())`). Leitura não precisa de lock.

**4. Endpoints em `pacientes.py`.**
- `GET /api/pacientes?cpf=`: lista com 0 ou 1 item, com `PacienteOut` + `atendimento_ativo: bool`. Lista em
  vez de 404 porque "não encontrado" é resultado normal da busca.
- `POST /api/pacientes/{id}/atendimentos`: perfil `enfermeiro`, o mesmo que cadastra. Cria o prontuário e a
  evolução "Cadastro". Responde 201 com `{prontuario_id, paciente_id, status}`.
- `GET /api/pacientes/{id}/atendimentos`: `ClinicoAtual`. Retorna os episódios com `status_atendimento =
  'alta'`, cada um com `data_entrada` (`data_criacao`), `data_alta` (data da evolução "Alta"),
  classificação, queixa, sinais vitais, evoluções e prescrições. O conteúdo vem embutido, em uma chamada só,
  porque o volume é pequeno. Alternativa considerada: endpoint de detalhe por episódio. Adiada até medir.

**5. Cadastro no front.**
`CadastroScreen` tenta `POST /pacientes`. Em 409, busca `GET /pacientes?cpf=`:
- sem atendimento ativo: mostra cartão com nome e nascimento e o botão "Abrir novo atendimento";
- com atendimento ativo: mostra "Paciente já está em atendimento".

Não há busca prévia por CPF a cada digitação; o caminho feliz (paciente novo) não muda.

**6. Histórico no posto.**
`AtendimentoScreen` faz `GET /atendimentos` junto com o prontuário. A seção aparece colapsada, com itens
resumidos e expansão por item usando estado local. Reaproveita os blocos de evolução e prescrição criados
em A.

## Risks / Trade-offs

- [Mudança de 404 para 409 em `get_prontuario_ativo` quando só há episódios com alta] → Hoje alta + ação já
  dá 409 pela checagem de transição. O único caso novo é triagem ou prescrição em paciente com alta, que
  antes era aceita indevidamente (prescrição após alta). É uma correção. Ajustar os testes que dependam
  disso.
- [Prescrição após alta deixa de ser possível] → Comportamento clinicamente correto; documentar.
- [Índice parcial é específico do PostgreSQL] → O projeto é só PostgreSQL. Os testes já rodam em Postgres
  no compose.
- [Histórico grande embutido] → Ponytail: sem paginação. Adicionar `limit` quando um paciente passar de
  algumas dezenas de visitas.

## Migration Plan

1. Rodar `alembic upgrade` (`0006`): cria o índice. Falha se houver 2 prontuários ativos para o mesmo
   paciente, o que não acontece hoje porque o cadastro cria 1.
2. Deploy do backend, depois do front.
3. Rollback: `alembic downgrade -1` remove o índice. O código antigo continua funcionando com dados 1:1. Se
   já houver pacientes com mais de um prontuário, o código antigo pega `.first()` e fica errado, então o
   rollback do backend após uso real exige cuidado.

## Open Questions

- Atualização de dados cadastrais no retorno (telefone ou endereço novos): incluir aqui ou abrir change
  separado? Proposta: separado.
