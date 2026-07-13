# Especificação de Requisitos

## 1. Requisitos Funcionais (RF)
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| RF001 | Autenticação | Login via matrícula funcional (6 dígitos) + PIN (4 dígitos). | Essencial |
| RF002 | Cadastro | Registro de pacientes com CNS/CPF. | Essencial |
| RF003 | Triagem | Registro de sinais vitais e cálculo automático da classificação de risco (Protocolo de Manchester). | Essencial |
| RF004 | Prontuário | Consulta de histórico clínico: sinais vitais, evolução e prescrições do paciente. | Essencial |
| RF005 | Prescrição | Registro de medicamento, dosagem, via e frequência pelo médico responsável. | Essencial |
| RF006 | Painel de Atendimento | Listagem de pacientes filtrável por classificação de risco, ordenada por gravidade. | Importante |

## 2. Requisitos Não Funcionais (RNF)
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF001 | Segurança | Criptografia AES-256 para dados sensíveis em repouso; PIN armazenado como hash (bcrypt/argon2). |
| RNF002 | LGPD | Auditoria de acesso a dados sensíveis. |
| RNF003 | Auditabilidade | Proibição de exclusão física de registros clínicos (soft delete via coluna `deleted_at`). |
| RNF004 | Usabilidade | Fluxo de triagem deve permitir calcular a classificação de risco em no máximo 3 passos (sinais vitais → calcular → confirmar). |

## 3. Detalhamento SDD (CARE)
Para cada requisito, a implementação deve seguir o padrão:

### [CARE-RF001] Autenticação por Matrícula/PIN
* **Context (Contexto)**: Colaborador cadastrado com matrícula e PIN (hash) definidos no sistema.
* **Action (Ação)**: Criar endpoint de autenticação que valide matrícula + PIN contra a tabela COLABORADOR (hash bcrypt/argon2).
* **Result (Resultado)**: Token JWT gerado após sucesso; Código 401 em falha (matrícula ou PIN inválidos).
* **Evaluation (Avaliação)**: Executar `npm test tests/auth.spec.ts` (deve passar com 100% de sucesso).

### [CARE-RF002] Cadastro de Pacientes
* **Context (Contexto)**: Esquema de banco de dados 'PACIENTE' criado.
* **Action (Ação)**: Criar endpoint POST `/api/pacientes` com validação de CPF e CNS.
* **Result (Resultado)**: Registro persistido no banco; Log de auditoria criado.
* **Evaluation (Avaliação)**: Validar contra JSON Schema definido em `04-modelo-dados.md`.

### [CARE-RF003] Triagem (Protocolo de Manchester)
* **Context (Contexto)**: Paciente com cadastro completo, aguardando triagem (ver UC001 em `03-casos-uso.md`).
* **Action (Ação)**: Registrar sinais vitais (PA, FC, FR, Temperatura, SpO2, dor 0-10) e aplicar a árvore de decisão do Protocolo de Manchester — critérios detalhados em `03-casos-uso.md` (UC001) — para calcular cor de risco, tempo-meta e justificativa.
* **Result (Resultado)**: Classificação de risco (Vermelho/Laranja/Amarelo/Verde/Azul) persistida no prontuário; paciente passa ao status "Aguardando Atendimento", ordenado no painel por gravidade.
* **Evaluation (Avaliação)**: Teste unitário deve cobrir os 5 cenários de cores com 100% de acurácia.

### [CARE-RF004] Consulta de Prontuário
* **Context (Contexto)**: Paciente com pelo menos um registro (cadastro, triagem ou atendimento) — ver UC002 em `03-casos-uso.md`.
* **Action (Ação)**: Buscar paciente por ID e compor view com sinais vitais mais recentes, linha do tempo de evolução (ordem cronológica decrescente) e prescrições.
* **Result (Resultado)**: Tela somente-leitura; ação "Nova Prescrição" visível apenas para perfil Médico.
* **Evaluation (Avaliação)**: Validar que paciente sem prescrições exibe "Nenhuma prescrição registrada." sem quebra de layout.

### [CARE-RF005] Prescrição
* **Context (Contexto)**: Usuário autenticado com perfil Médico; paciente selecionado — ver UC003 em `03-casos-uso.md`.
* **Action (Ação)**: Criar endpoint POST `/api/pacientes/{id}/prescricoes` com medicamento, dosagem, via (Oral/IV/IM/SC/Tópica), frequência e observações.
* **Result (Resultado)**: Prescrição persistida e vinculada ao prontuário e ao médico responsável; evolução clínica tipo "Prescrição" criada automaticamente.
* **Evaluation (Avaliação)**: Validar RBAC — perfil Enfermeiro não deve conseguir acessar o endpoint (403).

### [CARE-RF006] Painel de Atendimento
* **Context (Contexto)**: Usuário autenticado (Enfermeiro ou Médico) — ver UC006 em `03-casos-uso.md`.
* **Action (Ação)**: Listar pacientes ordenados por classificação de risco (Vermelho→Azul), com filtro opcional por cor.
* **Result (Resultado)**: Fila priorizada visualmente; ação "Fazer Triagem" visível apenas para pacientes "Aguardando Triagem" e perfil Enfermeiro.
* **Evaluation (Avaliação)**: Validar ordenação determinística por classificação e ausência de pacientes de outra cor quando o filtro está aplicado.