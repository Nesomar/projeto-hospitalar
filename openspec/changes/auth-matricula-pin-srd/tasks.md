## 1. Fundação de Dados

- [x] 1.1 Criar migrations PostgreSQL para `COLABORADOR`, `PACIENTE`, `PRONTUARIO`, `EVOLUCAO`, `PRESCRICAO` conforme `docs/04-modelo-dados.md`.
- [x] 1.2 Aplicar constraint de soft delete (`deleted_at`) em todas as tabelas — proibido `DELETE` físico (RNF003).
- [x] 1.3 Aplicar constraint de enum em `classificacao_risco` (`vermelho|laranja|amarelo|verde|azul`).

## 2. Autenticação (`autenticacao-matricula-pin`)

- [x] 2.1 Implementar hashing de PIN (bcrypt/argon2) e cadastro de `COLABORADOR`.
- [x] 2.2 Implementar endpoint de login que valida matrícula + PIN e emite JWT.
- [x] 2.3 Implementar middleware RBAC que restringe rotas por perfil (`enfermeiro`/`medico`).
- [x] 2.4 Testes cobrindo os cenários de `specs/autenticacao-matricula-pin/spec.md` (login sucesso/falha, PIN nunca em texto puro, RBAC prescrição).

## 3. Cadastro de Paciente (`cadastro-paciente`)

- [x] 3.1 Implementar endpoint `POST /api/pacientes` com validação de CPF (11 dígitos) e CNS (15 dígitos).
- [x] 3.2 Criar evolução automática do tipo "Cadastro" ao registrar paciente.
- [x] 3.3 Testes cobrindo os cenários de `specs/cadastro-paciente/spec.md`.

## 4. Triagem — Protocolo de Manchester (`triagem-manchester`)

- [ ] 4.1 Portar a lógica de `calcManchester` do protótipo (`docs/prototipo/projeto/Prototipo Hospitalar.dc.html`) para um serviço de back-end, seguindo a tabela de critérios em `docs/03-casos-uso.md` (UC001).
- [ ] 4.2 Implementar endpoint de cálculo/confirmação de triagem, com validação de campos obrigatórios (PA, FC, Temp, SpO2).
- [ ] 4.3 Ao confirmar, persistir `classificacao_risco` e atualizar status do paciente para "Aguardando Atendimento".
- [ ] 4.4 Testes cobrindo os 5 cenários de cor com 100% de acurácia (`specs/triagem-manchester/spec.md`).

## 5. Prontuário (`prontuario`)

- [ ] 5.1 Implementar endpoint de consulta de prontuário (sinais vitais, evoluções em ordem decrescente, prescrições).
- [ ] 5.2 Restringir exibição da ação "+ Nova Prescrição" ao perfil médico.
- [ ] 5.3 Testes cobrindo os cenários de `specs/prontuario/spec.md`.

## 6. Prescrição (`prescricao`)

- [ ] 6.1 Implementar endpoint `POST /api/pacientes/{id}/prescricoes` restrito a perfil médico (RBAC).
- [ ] 6.2 Criar evolução automática do tipo "Prescrição" ao registrar.
- [ ] 6.3 Testes cobrindo os cenários de `specs/prescricao/spec.md`.

## 7. Painel de Atendimento (`painel-atendimento`)

- [ ] 7.1 Implementar endpoint de listagem de pacientes com ordenação por gravidade e filtro por cor.
- [ ] 7.2 Restringir ação "Fazer Triagem" a pacientes "Aguardando Triagem" e perfil enfermeiro.
- [ ] 7.3 Testes cobrindo os cenários de `specs/painel-atendimento/spec.md`.

## 8. Front-end

- [ ] 8.1 Recriar as telas do protótipo (`docs/prototipo/projeto/Prototipo Hospitalar.dc.html`) em React, substituindo o estado mockado por chamadas à API real.
- [ ] 8.2 Atualizar tela de login para matrícula (6 dígitos) + PIN (4 dígitos), conforme já ajustado no protótipo.

## 9. Fechamento

- [ ] 9.1 Rodar `openspec validate auth-matricula-pin-srd` e corrigir eventuais erros de formatação das specs.
- [ ] 9.2 Sincronizar `docs/SPEC.md` (Task Breakdown) com o progresso desta mudança.
- [ ] 9.3 Arquivar a mudança (`openspec archive`) após validação em produção/homologação.
