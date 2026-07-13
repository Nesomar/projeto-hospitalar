## Why

O SRD (`docs/02-*` a `docs/07-*`) especificava login via LDAP/AD (RF001), o que pressupõe infraestrutura de domínio Active Directory inexistente neste projeto, e vinha com seções inteiras de placeholder não preenchidas (visão, requisitos além de RF001/RF002, casos de uso, interfaces). O protótipo interativo já implementa mais funcionalidades (triagem por Manchester, prontuário, prescrição, painel) do que o SRD documentava formalmente. É preciso simplificar a autenticação para matrícula+PIN (sem dependência de AD) e formalizar via OpenSpec as capacidades que o protótipo já demonstra, como base testável para a implementação real (fora do protótipo mockado).

## What Changes

- RF001 trocado de LDAP/AD para **matrícula (6 dígitos) + PIN (4 dígitos)**, com entidade `COLABORADOR` (matrícula, pin_hash, nome, perfil) sustentando o login.
- Protótipo interativo (`docs/prototipo/projeto/Prototipo Hospitalar.dc.html`) atualizado: campos de login, state e handlers renomeados de LDAP/senha para matrícula/PIN.
- SRD completado: RF003 (Triagem), RF004 (Prontuário), RF005 (Prescrição), RF006 (Painel de Atendimento), RNF003 (Auditabilidade/soft delete), RNF004 (Usabilidade), casos de uso UC001-UC006 com diagrama de casos de uso e diagrama de estado do status do paciente (mermaid), modelo de dados com entidades `COLABORADOR` e `PRESCRICAO` e diagrama ER completo, interface TypeScript de integração completa, arquitetura com diagrama de componentes (front-end/back-end/DB).
- **BREAKING**: nenhuma implementação de produção existe ainda — a mudança fixa matrícula+PIN como direção definitiva de autenticação, abandonando LDAP/AD como requisito.

## Capabilities

### New Capabilities
- `autenticacao-matricula-pin`: login de colaborador por matrícula (6 dígitos) + PIN (4 dígitos), com emissão de token JWT e RBAC por perfil (enfermeiro/médico).
- `cadastro-paciente`: registro de paciente com validação de CPF (11 dígitos) e CNS (15 dígitos).
- `triagem-manchester`: registro de sinais vitais (PA, FC, FR, Temp, SpO2, dor) e cálculo automático da classificação de risco pelo Protocolo de Manchester.
- `prontuario`: consulta somente-leitura de histórico clínico — sinais vitais, linha do tempo de evolução e prescrições do paciente.
- `prescricao`: registro de prescrição médica (medicamento, dosagem, via, frequência) vinculada ao prontuário e ao médico responsável.
- `painel-atendimento`: listagem de pacientes filtrável por classificação de risco e ordenada por gravidade.

### Modified Capabilities
- Nenhuma — não existiam specs formais em `openspec/specs/` antes desta mudança.

## Impact

- `docs/02-requisitos.md`, `docs/03-casos-uso.md`, `docs/04-modelo-dados.md`, `docs/05-interfaces.md`, `docs/06-arquitetura.md`, `docs/07-glossario.md`, `docs/SPEC.md`, `docs/01-visao.md` (SRD, já atualizados nesta sessão).
- `docs/prototipo/projeto/Prototipo Hospitalar.dc.html` (protótipo mock, já atualizado nesta sessão).
- Futura implementação real: back-end Python/FastAPI + PostgreSQL, front-end React (ver `06-arquitetura.md`) — ainda não iniciada.
