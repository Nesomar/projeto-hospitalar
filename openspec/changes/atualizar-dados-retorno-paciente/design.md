## Context

O retorno de paciente (change `episodios-atendimento`) abre novo atendimento via
`POST /api/pacientes/{id}/atendimentos`, sem corpo. O cartão de retorno em `CadastroScreen` mostra nome e
nascimento e só oferece "Abrir novo atendimento". `GET /api/pacientes?cpf=` já devolve `PacienteOut`
(com `telefone` e `sexo`), então o front tem os valores atuais.

O modelo `Paciente` tem `nome`, `cpf`, `cns`, `data_nascimento`, `sexo` e `telefone`. Não há endereço.

## Goals / Non-Goals

**Goals:**
- Enfermeiro corrige telefone e sexo no momento do retorno, sem sair do fluxo.
- Atualização atômica com a abertura do atendimento e rastreável pela evolução "Cadastro".

**Non-Goals:**
- Editar nome, data de nascimento, CPF ou CNS. São identificadores; correção é fluxo administrativo.
- Adicionar endereço ao modelo. Exige migração e é outro change.
- Edição de cadastro fora do retorno (ex.: paciente em atendimento). Sem demanda hoje.
- Tabela de auditoria de alterações cadastrais.

## Decisions

**1. Estender `POST /atendimentos` com `dados_cadastrais` opcional, em vez de criar `PATCH /pacientes/{id}`.**
A necessidade é "atualizar no retorno". Um endpoint de edição livre abriria o caso de editar paciente em
atendimento e exigiria regras de permissão e auditoria próprias. Com o corpo opcional, a atualização só
existe junto da abertura, na mesma transação, e o endpoint continua restrito ao enfermeiro. Alternativa
considerada: `PATCH` seguido de `POST`. Rejeitada porque dois requests deixam estado parcial (dado
atualizado sem atendimento aberto) e duplicam a checagem de permissão.

**2. Só `telefone` e `sexo`.**
São os dados que mudam sem afetar identidade. Schema `DadosCadastraisRetorno` com ambos opcionais;
`sexo` restrito a `F|M|O` (mesmos valores do select do cadastro). `telefone` livre, como no cadastro. O campo
ausente significa "não alterar". Limpar o telefone (valor `null` explícito) não é suportado: o front sempre
envia o valor atual ou o novo.

**3. Rastreabilidade na evolução "Cadastro".**
Se algum campo mudou, a descrição vira "Retorno do paciente, aguardando triagem. Dados atualizados:
telefone, sexo." (só os que mudaram). A evolução já carrega `responsavel_matricula`, que é o guardrail do
projeto. Os valores antigo e novo não são gravados (dado pessoal desnecessário no log); só o nome do campo.

**4. Ordem dentro do endpoint.**
Valida paciente (404) e atendimento ativo (409) antes de tocar no paciente. Depois cria o prontuário com
flush (o índice único ainda fecha a corrida), aplica a atualização e faz um único commit. Em
`IntegrityError` o rollback desfaz tudo, inclusive a atualização.

**5. Front.**
O cartão de retorno ganha input de telefone e select de sexo, preenchidos com os valores de `retorno`. O
clique em "Abrir novo atendimento" envia `dados_cadastrais` com os valores do formulário. O backend
descarta o que não mudou, então o front não precisa comparar. Com atendimento ativo, os campos não aparecem.

## Risks / Trade-offs

- [Enfermeiro sobrescreve telefone certo por engano] → Campos vêm preenchidos e a mudança fica registrada na
  evolução com a matrícula. Valores antigos não ficam gravados; aceito porque não há demanda de auditoria
  detalhada.
- [`sexo` do cadastro original é texto livre, pode haver valor fora de `F|M|O` no banco] → O select do front
  só envia `F|M|O`. Se o valor atual for outro, o select abre em branco e o campo só é enviado se o enfermeiro
  escolher uma opção.
- [Corpo opcional em POST] → Compatível com clientes atuais; sem corpo, nada muda.

## Open Questions

- Incluir endereço no cadastro e no retorno? Proposta: change separado, junto da migração.
