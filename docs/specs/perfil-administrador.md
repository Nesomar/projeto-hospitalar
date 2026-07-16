---
feature: perfil-administrador
status: READY_FOR_REVIEW
created: 2026-07-15
---

# Perfil de Administrador e Cadastro de Colaboradores

## Objetivo
Hoje o sistema só reconhece os perfis `enfermeiro` e `medico`, e o cadastro de novos
colaboradores é feito por um endpoint que qualquer colaborador autenticado (enfermeiro ou
médico) pode chamar — não existe nenhum controle de quem pode dar acesso ao sistema a
alguém, e não existe forma oficial de criar o primeiro usuário sem mexer direto no banco.
Esta feature introduz um perfil `administrador`, restringe o cadastro de novos
colaboradores (enfermeiros e médicos) a esse perfil, e fornece um script de bootstrap para
criar o primeiro administrador do sistema. O valor é ter uma trilha clara de "quem pode dar
acesso a quem" e eliminar a brecha atual em que qualquer colaborador logado cadastra outro.

## Escopo
### Incluído
- Novo perfil `administrador`, reconhecido pelo login e pelo controle de acesso (RBAC) do
  sistema, com uma área de gestão própria.
- Cadastro de colaboradores com perfil `enfermeiro` ou `medico` restrito a usuários
  autenticados com perfil `administrador` (via tela na área de gestão e via ação
  correspondente no backend).
- Restrição de acesso: perfis `enfermeiro` e `medico` deixam de conseguir cadastrar
  colaboradores (fecha o comportamento atual, que é aberto a qualquer autenticado).
- Restrição de acesso: perfil `administrador` não acessa as telas/ações clínicas
  exclusivas de enfermeiro/médico (triagem, prontuário, prescrição, painel de atendimento).
- Script de bootstrap (linha de comando, executado fora da API) para cadastrar o primeiro
  administrador do sistema, sem depender de já existir alguém autenticado.

### Fora do escopo
- Edição, inativação (soft delete) ou listagem de colaboradores já cadastrados — esta
  feature cobre apenas a criação de novos enfermeiros/médicos pelo administrador.
- Cadastro de um segundo (ou N-ésimo) administrador pela interface/API — nesta primeira
  versão, administradores adicionais só são criados repetindo o script de bootstrap
  (ver "Perguntas em aberto").
- Recuperação de PIN / reset de senha para qualquer perfil, incluindo o administrador.
- Qualquer alteração no fluxo clínico já existente (triagem, prontuário, prescrição,
  painel de atendimento) além da restrição de acesso do perfil `administrador` a essas
  telas.

## Comportamento esperado

### Login e identificação do perfil
- O administrador se autentica pelo mesmo fluxo já existente no sistema: matrícula
  (6 dígitos) + PIN (4 dígitos).
- Após autenticar, um usuário com perfil `administrador` é direcionado à área de gestão
  de colaboradores, não ao painel de atendimento clínico.
- Usuários com perfil `enfermeiro` ou `medico` continuam sendo direcionados ao fluxo
  clínico existente e não enxergam a área de gestão.

### Área de gestão — cadastro de enfermeiros e médicos
- Só um usuário autenticado com perfil `administrador` acessa a área de gestão e a ação
  de cadastro de colaborador.
- O formulário/ação de cadastro pede: matrícula (6 dígitos numéricos), PIN inicial
  (4 dígitos numéricos), nome completo e perfil do novo colaborador — sendo o perfil
  limitado às opções `enfermeiro` ou `medico` (o formulário não oferece `administrador`
  como opção).
- Ao confirmar, o sistema valida os campos, garante que a matrícula ainda não está em uso
  (por qualquer colaborador, ativo ou inativado) e cria o colaborador com o PIN
  informado, já pronto para fazer login imediatamente com essas credenciais.
- Em caso de sucesso, o administrador recebe confirmação e pode cadastrar outro
  colaborador em seguida.
- Em caso de erro de validação (formato de matrícula/PIN, campo obrigatório vazio) ou de
  matrícula duplicada, o sistema informa o motivo de forma clara e nenhum registro é
  persistido.

### Restrição de acesso cruzada entre perfis
- Enfermeiros e médicos não veem a opção de cadastro de colaborador em nenhuma tela e,
  se tentarem chamar a ação diretamente, recebem erro de permissão.
- Administradores não veem nem conseguem executar as ações clínicas exclusivas de
  enfermeiro/médico (fazer triagem, consultar prontuário, prescrever, consultar painel
  de atendimento); ao tentar, recebem erro de permissão.
- Usuários não autenticados não acessam nenhuma ação de cadastro de colaborador nem a
  área de gestão.

### Script de bootstrap do primeiro administrador
- Existe um script executável por linha de comando (fora da API HTTP) que recebe
  matrícula, PIN, nome e cria um colaborador com perfil `administrador`.
- O script pode ser executado a qualquer momento (não só quando o banco está vazio), mas
  falha de forma clara se a matrícula informada já estiver em uso — não duplica nem
  sobrescreve colaborador existente.
- O colaborador criado pelo script consegue se autenticar normalmente pelo fluxo de login
  padrão do sistema, com a matrícula e o PIN informados na execução.

## Critérios de aceite
- [ ] AC-1: Administrador autenticado acessa a área de gestão de colaboradores; enfermeiro
  ou médico autenticado recebe erro de permissão (403) ao tentar acessar a área de gestão
  ou a ação de cadastro de colaborador.
- [ ] AC-2: Administrador autenticado cadastra um novo colaborador informando matrícula,
  PIN, nome e perfil (`enfermeiro` ou `medico`); o colaborador criado consegue se
  autenticar em seguida com essas mesmas credenciais.
- [ ] AC-3: Tentativa de cadastrar um colaborador com perfil `administrador` pela ação de
  cadastro de enfermeiros/médicos é rejeitada — `administrador` não é uma opção válida
  nesse fluxo.
- [ ] AC-4: Cadastro com matrícula já usada por outro colaborador (ativo ou já inativado)
  é rejeitado com mensagem de erro, sem criar/duplicar registro.
- [ ] AC-5: Cadastro com matrícula fora do padrão (diferente de 6 dígitos numéricos) ou
  PIN fora do padrão (diferente de 4 dígitos numéricos) é rejeitado com mensagem de
  validação, sem persistir registro.
- [ ] AC-6: Usuário não autenticado não consegue executar a ação de cadastro de
  colaborador nem acessar a área de gestão (erro de autenticação, 401).
- [ ] AC-7: O script de bootstrap, executado informando matrícula, PIN, nome e perfil
  administrador, cria o colaborador com sucesso e este consegue se autenticar pelo login
  padrão do sistema logo em seguida.
- [ ] AC-8: O script de bootstrap, executado com uma matrícula já cadastrada (por
  qualquer colaborador, de qualquer perfil), falha com mensagem de erro clara e não
  duplica nem altera o registro existente.
- [ ] AC-9: Administrador autenticado recebe erro de permissão (403) ao tentar executar
  qualquer ação clínica exclusiva de enfermeiro/médico (fazer triagem, consultar
  prontuário, prescrever, consultar painel de atendimento).
- [ ] AC-10: Enfermeiro ou médico autenticado recebe erro de permissão (403) ao tentar
  chamar diretamente a ação de cadastro de colaborador, mesmo sem passar pela tela da
  área de gestão.

## Casos de borda e erros
- Nome do colaborador vazio ou composto só por espaços — deve ser rejeitado como campo
  obrigatório.
- Duas tentativas simultâneas de cadastro com a mesma matrícula — apenas uma deve ter
  sucesso; a outra recebe erro de matrícula duplicada, sem gerar dois registros.
- PIN ou matrícula contendo caracteres não numéricos — rejeitado na validação, sem chegar
  a persistir.
- Token de sessão expirado ou inválido ao tentar acessar a área de gestão ou cadastrar
  colaborador — tratado como não autenticado (401), sem vazar informação sobre o motivo
  exato da invalidez.
- Execução do script de bootstrap mais de uma vez, inclusive repetindo a mesma matrícula
  usada anteriormente — deve falhar de forma idempotente (sem duplicar) na segunda
  execução.
- Execução do script de bootstrap informando matrícula/PIN fora do padrão de dígitos —
  deve falhar com mensagem clara antes de tentar persistir.

## Perguntas em aberto

Todas as perguntas abaixo foram decididas nesta rodada de validação técnica (não havia
usuário disponível para confirmar) — a justificativa completa de cada decisão está em
"Detalhes Técnicos > Decisões e riscos". Resumo das decisões:

- Administrador cadastrar outro administrador pela UI? **Decidido: não.** O endpoint
  `POST /api/colaboradores` fica restrito a criar apenas `enfermeiro`/`medico`
  (`require_perfil("administrador")` no endpoint + validação de `perfil` limitada a esse
  subconjunto no payload). Administradores adicionais só são criados repetindo o script
  de bootstrap. Reduz superfície de escalonamento de privilégio pela UI e é consistente
  com o pedido original ("cadastrar enfermeiros e médicos").
- Rastrear qual administrador cadastrou cada colaborador? **Decidido: sim.** Novo campo
  `colaboradores.criado_por_matricula` (nullable, FK para `colaboradores.matricula`),
  seguindo o mesmo padrão de FK usado em `responsavel_matricula` (evolução/prescrição).
  Nullable porque colaboradores criados pelo script de bootstrap não têm um administrador
  autenticado por trás.
- Edição/inativação/listagem de colaboradores ficam para depois? **Decidido: sim, fora de
  escopo desta feature** — registrar como próxima feature (backlog).
- Script de bootstrap dedicado vs reaproveitar `seed_colaborador.py`? **Decidido:
  reaproveitar sem alterações.** O script já aceita `--perfil` com `choices=PERFIS_COLABORADOR`
  e já trata duplicidade de matrícula (inclusive soft-deletada) como erro — ao incluir
  `"administrador"` em `PERFIS_COLABORADOR` (mudança no model), o script passa a suportar
  `--perfil administrador` automaticamente, sem nenhuma alteração de código nele.

## Detalhes Técnicos

### Stack detectada
- Backend: Python / FastAPI, SQLAlchemy + Alembic, PostgreSQL 16 (`docker-compose.yml`),
  auth JWT (`python-jose`) + bcrypt (`app/core/security.py`).
- Frontend: React (componentes funcionais, hooks, sem router — troca de tela via estado
  em `App.jsx`), estilos inline com tokens em `frontend/src/styles.js` e `colors.js`.

### Contrato de API (fonte de verdade entre back e front)

#### `POST /api/colaboradores` (rota existente, comportamento alterado)
- Auth: Bearer token obrigatório; perfil deve ser `administrador`
  (`Depends(require_perfil("administrador"))`, mesmo padrão de `MedicoAtual` em
  `atendimento.py`/`prescricao.py`).
- Request body:
  ```json
  { "matricula": "123456", "pin": "1234", "nome": "Fulano de Tal", "perfil": "enfermeiro" }
  ```
  - `matricula`: string, regex `^[0-9]{6}$` (`MATRICULA_PATTERN`, já existe).
  - `pin`: string, regex `^[0-9]{4}$` (`PIN_PATTERN`, já existe).
  - `nome`: string, não vazia após `strip()` (validação nova — hoje só existe
    `min_length=1`, que não barra string só com espaços).
  - `perfil`: enum restrito a `"enfermeiro" | "medico"` — **não** ao `PERFIS_COLABORADOR`
    completo do model (que passa a incluir `"administrador"`). Novo conjunto
    `PERFIS_CADASTRAVEIS = ("enfermeiro", "medico")` em `app/schemas/colaborador.py`.
- Response `201 Created`: `ColaboradorOut` — `{ id, matricula, nome, perfil }` (inalterado;
  `criado_por_matricula` não é exposto na resposta, escopo desta feature não inclui
  listagem/auditoria via API).
- Erros:
  - `401 Unauthorized` — sem token, token inválido/expirado (`get_current_colaborador`,
    inalterado).
  - `403 Forbidden` — autenticado mas perfil ≠ `administrador` (`"Perfil sem permissão
    para esta ação"`, mensagem padrão de `require_perfil`).
  - `422 Unprocessable Entity` — matrícula/PIN fora do padrão, nome vazio/só espaços,
    `perfil` fora de `{enfermeiro, medico}` (inclui tentativa de enviar `"administrador"`
    — cobre AC-3).
  - `409 Conflict` — matrícula já em uso, ativa ou soft-deletada (`"Matrícula já
    cadastrada"`; checagem prévia + `IntegrityError` como rede de segurança para a corrida
    de duas requisições simultâneas — padrão já existente na rota).

Nenhum outro endpoint novo é necessário: a "área de gestão" no escopo desta feature é
só a tela de cadastro acima; login, listagem do painel de colaboradores etc. não fazem
parte do escopo (ver "Fora do escopo").

#### Efeito colateral obrigatório do novo perfil nos endpoints clínicos existentes (AC-9)
Hoje `pacientes.py`, `painel.py`, `prontuario.py` e `triagem.py` usam a dependência
`CurrentColaborador` (qualquer perfil autenticado, sem restrição) — só `atendimento.py` e
`prescricao.py` já restringem a `medico` via `require_perfil("medico")`. Sem alteração,
um `administrador` autenticado passaria a acessar `POST /api/pacientes`,
`GET /api/painel`, `GET /api/pacientes/{id}/prontuario`, `POST /api/triagem/calcular` e
`POST /api/pacientes/{id}/triagem/confirmar` assim que `"administrador"` virar um perfil
autenticável — violando AC-9. **Correção obrigatória**: trocar `CurrentColaborador` por
um novo alias `ClinicoAtual = Annotated[Colaborador, Depends(require_perfil("enfermeiro",
"medico"))]` (mesmo padrão de `MedicoAtual`) nesses quatro arquivos. `atendimento.py` e
`prescricao.py` não precisam de nenhuma mudança (já restritos a `medico`, que já exclui
`administrador`).

### Backend
- **Modelo de dados**:
  - `backend/app/models/colaborador.py`: `PERFIS_COLABORADOR = ("enfermeiro", "medico",
    "administrador")`; novo campo `criado_por_matricula = Column(String(6),
    ForeignKey("colaboradores.matricula"), nullable=True)` (nullable pelo motivo descrito
    nas decisões — colaborador criado pelo script de bootstrap não tem administrador
    autenticado por trás).
  - **Migração Alembic** nova (`backend/alembic/versions/0004_perfil_administrador.py`,
    `down_revision = "0003_status_atendimento"`):
    - `ALTER TYPE perfil_colaborador ADD VALUE 'administrador'` via `op.execute(...)`.
      Postgres 16 (imagem do `docker-compose.yml`) já suporta `ADD VALUE` dentro de
      transação desde a v12, então não precisa de `autocommit_block()` — só não se pode
      usar o valor novo na mesma transação em que foi criado, o que não é o caso aqui.
      `downgrade()` documentado como não suportado (Postgres não permite remover valor de
      enum de forma trivial) — mesma limitação inerente ao tipo, não uma escolha da
      feature.
    - `op.add_column("colaboradores", sa.Column("criado_por_matricula", sa.String(6),
      sa.ForeignKey("colaboradores.matricula"), nullable=True))`.
  - Sem alteração em nenhuma outra tabela.
- **Camadas/módulos afetados**:
  - `backend/app/models/colaborador.py` — enum + campo novo (acima).
  - `backend/app/schemas/colaborador.py` — `PERFIS_CADASTRAVEIS`, `field_validator` de
    `perfil` trocado para validar contra esse subconjunto, novo `field_validator` de
    `nome` (`strip()` + rejeitar vazio).
  - `backend/app/api/routes/auth.py` — `cadastrar_colaborador` passa a exigir
    `require_perfil("administrador")` em vez de `CurrentColaborador`; grava
    `criado_por_matricula=colaborador.matricula` no `Colaborador` criado.
  - `backend/app/api/deps.py` — sem alteração (`require_perfil` já existe e é reaproveitado
    como está).
  - `backend/app/api/routes/pacientes.py`, `painel.py`, `prontuario.py`, `triagem.py` —
    trocar `CurrentColaborador` por `ClinicoAtual` (novo alias, ver seção anterior).
  - `backend/scripts/seed_colaborador.py` — sem alteração de código (já suporta
    `--perfil administrador` assim que o enum do model incluir esse valor); script criado
    grava `criado_por_matricula=None` implicitamente (campo não passado ao `Colaborador(...)`).
- **Padrões obrigatórios**:
  - RBAC via `require_perfil`, reaproveitando o padrão já usado em `atendimento.py`.
  - Sem `DELETE` físico — feature não introduz nenhum delete; `criado_por_matricula` não
    afeta o soft delete existente de `colaboradores.deleted_at`.
  - Sem secret em código — nenhuma configuração nova introduzida por esta feature.
  - `IntegrityError` como rede de segurança para corrida de matrícula duplicada (padrão
    já existente em `cadastrar_colaborador`, mantido).
  - Mensagens de erro sem vazar detalhe de autenticação (`401` genérico já existente em
    `get_current_colaborador`, reaproveitado sem alteração).

### Frontend
- **Telas/componentes afetados**:
  - Nova tela `frontend/src/screens/GestaoColaboradoresScreen.jsx` — formulário de
    cadastro (matrícula, PIN, nome, `select` perfil limitado a Enfermeiro/Médico),
    seguindo o mesmo padrão visual e de validação client-side de
    `frontend/src/screens/CadastroScreen.jsx` (usa `s.field`, `s.label`, `s.input`,
    `s.errorText`, `s.btnPrimary` de `styles.js`).
  - `frontend/src/components/Shell.jsx`:
    - `NAV_POR_PERFIL.administrador = [{ key: "gestao", label: "Cadastro de Colaborador" }]`.
    - `TITULOS.gestao = { _: ["Cadastro de Colaborador", "Registro de novo enfermeiro ou médico no sistema."] }`.
    - `LABEL_PERFIL.administrador = "Administrador"`.
  - `frontend/src/App.jsx`:
    - Import e novo case `{screen === "gestao" && <GestaoColaboradoresScreen ... />}`.
    - `onLoginSuccess` roteia por perfil em vez de sempre ir para `"painel"`:
      `irPara(perfil === "administrador" ? "gestao" : "painel")` — administrador não tem
      painel clínico (AC-1/comportamento de login).
  - `frontend/src/api.js` — nova função `cadastrarColaborador(token, dados)` →
    `POST /api/colaboradores`, mesmo padrão de `cadastrarPaciente`.
- **Estado e integração com o contrato de API**: formulário local (`useState`, sem lib de
  formulário — não há nenhuma no projeto, ladder rung 2/3: reaproveitar padrão local já
  usado em `CadastroScreen.jsx`). Validação client-side espelha o contrato (regex
  matrícula/PIN, nome não vazio) só para feedback imediato; o backend é a fonte de
  verdade (erros `422`/`409` tratados via `ApiError` + `showToast`, padrão já existente em
  `api.js`/`CadastroScreen.jsx`).
- **Padrões obrigatórios**: reaproveitar `styles.js`/`colors.js` (nenhum novo token de
  design), `Toast.jsx` para feedback de sucesso/erro, `ApiError`/`setUnauthorizedHandler`
  já existentes em `api.js` para 401/403 (403 já cai no fluxo genérico de `showToast(err.message)`,
  não precisa de tratamento especial).

### Decisões e riscos (mini-ADR)
- Decisão: cadastro de administrador só via script — Motivo: pedido original menciona só
  "enfermeiros e médicos"; menor superfície de escalonamento de privilégio via UI —
  Alternativa descartada: permitir `administrador` no `perfil` do endpoint, mais flexível
  mas abre caminho pra um admin comprometido criar outros admins pela API sem trilha de
  bootstrap.
- Decisão: `criado_por_matricula` nullable em vez de obrigatório como
  `responsavel_matricula` — Motivo: guardrail de `responsavel_matricula` obrigatório
  (CLAUDE.md) é especificamente sobre evolução/prescrição (ação clínica com ator sempre
  autenticado); aqui o script de bootstrap legitimamente não tem ator autenticado —
  Alternativa descartada: coluna obrigatória com sentinela (ex. matrícula fixa "sistema"),
  mais complexa e sem ganho real de auditoria.
- Decisão: reaproveitar `seed_colaborador.py` em vez de script dedicado — Motivo: já
  genérico o suficiente (aceita `--perfil` por `choices`), zero mudança de código
  necessária — Alternativa descartada: script `seed_administrador.py` dedicado, seria
  duplicação sem ganho.
- Riscos:
  - Migração de enum é irreversível na prática (`downgrade()` de `ADD VALUE` não é
    suportado nativamente pelo Postgres) — aceitável pra este tipo de mudança aditiva, mas
    documentar explicitamente no arquivo de migração pra não surpreender em rollback.
  - A troca de `CurrentColaborador` por `ClinicoAtual` em 4 rotas é uma mudança
    cross-cutting fora do que o spec-writer tinha mapeado inicialmente (que só cobriu
    `auth.py`) — é obrigatória pra AC-9 passar; sem ela, administrador acessaria painel/
    prontuário/triagem/cadastro de paciente normalmente.
  - Validação de "nome só com espaços" não existe hoje em `ColaboradorCreate` — é gap
    novo introduzido pelos critérios de aceite desta feature (AC/casos de borda), não bug
    pré-existente a corrigir em outro lugar.

### Plano de implementação sugerido
- Backend:
  1. Model: adicionar `"administrador"` a `PERFIS_COLABORADOR` e coluna `criado_por_matricula`.
  2. Migração Alembic `0004_perfil_administrador` (enum + coluna).
  3. Schema: `PERFIS_CADASTRAVEIS`, validators de `perfil` e `nome` em `ColaboradorCreate`.
  4. Rota `auth.py`: `require_perfil("administrador")` + gravar `criado_por_matricula`.
  5. Trocar `CurrentColaborador` → `ClinicoAtual` em `pacientes.py`, `painel.py`,
     `prontuario.py`, `triagem.py`.
  6. Testes: AC-1 a AC-10 e casos de borda listados na spec.
- Frontend:
  1. `api.js`: `cadastrarColaborador`.
  2. `GestaoColaboradoresScreen.jsx` (form + validação client-side, seguindo
     `CadastroScreen.jsx`).
  3. `Shell.jsx`: nav/título/label do perfil `administrador`.
  4. `App.jsx`: rota `"gestao"` + redirecionamento pós-login por perfil.

### Nota de progresso — frontend done (2026-07-15)
Frontend implementado e validado (`npx oxlint` sem erros, `npm run build` ok). Arquivos
alterados/criados:
- `frontend/src/api.js` — `cadastrarColaborador(token, dados)`.
- `frontend/src/screens/GestaoColaboradoresScreen.jsx` (novo) — form de cadastro de
  colaborador.
- `frontend/src/components/Shell.jsx` — `NAV_POR_PERFIL.administrador`, `TITULOS.gestao`,
  `LABEL_PERFIL.administrador`.
- `frontend/src/App.jsx` — import + case `"gestao"`, roteamento pós-login por perfil
  (`onLoginSuccess`) e estado inicial de tela (`useState` de `screen`) considerando sessão
  de administrador já existente no `localStorage` ao recarregar a página.

### Nota de progresso — backend done (2026-07-15)
Backend implementado conforme "Detalhes Técnicos > Backend" acima. Arquivos
alterados/criados:
- `backend/app/models/colaborador.py` — `PERFIS_COLABORADOR` inclui `"administrador"`;
  coluna nova `criado_por_matricula` (FK pra `colaboradores.matricula`, nullable).
- `backend/alembic/versions/0004_perfil_administrador.py` (novo) — `ALTER TYPE ... ADD
  VALUE 'administrador'` + `add_column("criado_por_matricula")`; `downgrade()` documentado
  como não suportado para o enum (limitação nativa do Postgres).
- `backend/app/schemas/colaborador.py` — `PERFIS_CADASTRAVEIS = ("enfermeiro", "medico")`;
  `perfil_valido` validando contra esse subconjunto; novo validator `nome_nao_vazio`
  (`strip()` + rejeita vazio).
- `backend/app/api/routes/auth.py` — `cadastrar_colaborador` agora exige
  `require_perfil("administrador")` (alias local `AdministradorAtual`, mesmo padrão de
  `MedicoAtual`); grava `criado_por_matricula=admin.matricula`.
- `backend/app/api/deps.py` — novo alias `ClinicoAtual = Annotated[Colaborador,
  Depends(require_perfil("enfermeiro", "medico"))]`.
- `backend/app/api/routes/pacientes.py`, `painel.py`, `prontuario.py`, `triagem.py` —
  `CurrentColaborador` trocado por `ClinicoAtual` (bloqueia `administrador` dessas rotas).
- `backend/scripts/seed_colaborador.py` — sem alteração de código; validado que
  `--perfil administrador` já funciona (choices vem de `PERFIS_COLABORADOR`).
- `backend/app/api/routes/atendimento.py`, `prescricao.py` — sem alteração (já restritos a
  `require_perfil("medico")`, conforme spec).

Build/validação: sem ferramenta de lint configurada no projeto (`requirements-dev.txt` só
tem `pytest`/`httpx`); validado via `python -m py_compile` nos arquivos alterados, import
completo de `app.main:app` (16 rotas registradas), `alembic heads`/`history` (cadeia de
migração íntegra, head único `0004_perfil_administrador`) e `python -m pytest` (72 passed,
9 failed — todas as 9 falhas são em `tests/test_auth.py`, pré-existentes, esperadas pela
mudança de contrato: a fixture `auth_headers` em `tests/conftest.py` bootstrap um
colaborador `perfil="medico"`, que agora corretamente recebe `403` de
`POST /api/colaboradores` — comportamento novo é intencional (AC-10); fixture/testes
precisam ser atualizados pelo agente tester para usar `perfil="administrador"` no bootstrap
de `auth_headers` e cobrir os novos ACs).

Backend e frontend concluídos — status promovido a `READY_FOR_TESTS`.

### Nota de progresso — testes (2026-07-15)
Corrigida a fixture `auth_headers` (`backend/tests/conftest.py`), que fazia bootstrap
com `perfil="medico"` e por isso quebrava com o novo RBAC de
`POST /api/colaboradores`. `auth_headers` foi mantida com `perfil="medico"` (é usada
por toda a suíte clínica pré-existente — `pacientes`, `painel`, `prontuario`,
`triagem`, `atendimento`, `prescricao` — que continua exigindo apenas
enfermeiro/médico via `ClinicoAtual`) e uma nova fixture `admin_headers`
(`perfil="administrador"`) foi adicionada para os testes de cadastro de
colaborador. Os 9 testes de `test_auth.py` que falhavam por causa disso foram
migrados de `auth_headers` para `admin_headers` (comportamento de RBAC em si não
mudou de código — só a fixture de teste estava desatualizada).

Testes novos:
- `backend/tests/test_perfil_administrador.py` — AC-1, AC-2, AC-3, AC-4 (matrícula
  soft-deletada), AC-5 (nome vazio/só espaços), AC-6 (token inválido/ausente), AC-9
  (administrador barrado em pacientes/painel/triagem/prontuário/prescrição).
- `backend/tests/test_seed_colaborador.py` — AC-7 (bootstrap cria administrador
  funcional), AC-8 (matrícula duplicada falha sem duplicar, inclusive de outro
  perfil), casos de borda (execução repetida idempotente, matrícula/PIN fora do
  padrão falham antes de persistir).

Suíte backend completa: `python -m pytest` → **102 passed, 0 failed** (0 skipped).

Frontend: projeto não tem framework de teste configurado (`package.json` só tem
`dev/build/lint/preview`, sem Vitest/Jest/Testing Library e sem nenhum arquivo
`*.test.*`/`*.spec.*` no repo) — não foi introduzido um framework novo para esta
feature (fora do escopo de QA, decisão de arquitetura de projeto). Validado via
`npm run lint` (oxlint, 0 erros) e `npm run build` (build de produção ok) e via
leitura de código: `NAV_POR_PERFIL`/`TITULOS` em `Shell.jsx` só expõe "Cadastro de
Colaborador" para `administrador` e nunca para `enfermeiro`/`medico`; o app não tem
router nem navegação por URL (troca de tela 100% via `useState` em `App.jsx`,
disparada só por clique nos botões de nav filtrados por perfil), então
enfermeiro/médico não têm caminho de UI para alcançar a tela `gestao` — e, mesmo que
alcançassem, a chamada `cadastrarColaborador` bateria no `POST /api/colaboradores`
real e receberia 403 do backend (`GestaoColaboradoresScreen.onSubmit` trata qualquer
erro da API via `showToast(err.message)`, cobrindo 401/403/422/409 genericamente).
`onLoginSuccess` e o `useState` inicial de `screen` em `App.jsx` roteiam
`administrador` para `"gestao"` e os demais perfis para `"painel"`, cobrindo AC-1 do
lado do frontend.

Status promovido a `READY_FOR_REVIEW`.
