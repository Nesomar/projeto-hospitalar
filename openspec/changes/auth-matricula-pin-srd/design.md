## Context

Projeto UPA Nordeste é doc-driven (SDD): não existe código de aplicação real ainda, só o SRD (`docs/`) e um protótipo mockado em HTML/JS (`docs/prototipo/projeto/Prototipo Hospitalar.dc.html`) com dados em memória e toda a lógica de negócio simulada no client (`calcManchester`, formatação de CPF/CNS). Esta mudança formaliza, via OpenSpec, as capacidades que o protótipo já demonstra, com a decisão de autenticação simplificada (matrícula+PIN em vez de LDAP/AD) já refletida no SRD e no protótipo.

## Goals / Non-Goals

**Goals:**
- Definir specs testáveis (Requirement/Scenario) para as 6 capacidades já cobertas pelo protótipo e SRD.
- Registrar a decisão de autenticação por matrícula+PIN como direção definitiva, com o schema de dados (entidade COLABORADOR) que a sustenta.
- Servir de base para uma futura implementação real (back-end Python/FastAPI + PostgreSQL, front-end React) fiel ao comportamento do protótipo.

**Non-Goals:**
- Implementar o back-end/front-end real — este change só formaliza specs a partir do que já existe em docs/protótipo.
- Integração real com AGHU/HIS (fora de escopo, ver `01-visao.md`).
- MFA — explicitamente adiado (ver `06-arquitetura.md`, seção Acessos).

## Decisions

1. **Matrícula (6 dígitos) + PIN (4 dígitos) em vez de LDAP/AD.**
   Rationale: o projeto não tem infraestrutura de domínio AD; matrícula+PIN é rápido de digitar em terminal compartilhado (posto de enfermagem), padrão comum em sistemas hospitalares internos.
   Alternativas consideradas: email+senha local (mais robusto, porém mais fricção de digitação); acesso sem login (descartado — RF004/RF005 exigem rastrear o responsável por cada evolução/prescrição).

2. **PIN armazenado apenas como hash** (bcrypt/argon2), nunca em texto puro (RNF001, regra de integridade em `04-modelo-dados.md`).

3. **Classificação de risco (Manchester) como snapshot único no PRONTUARIO**, não versionado por evolução — espelha o protótipo, em que `sinaisVitais`/`classificacao` do paciente são únicos e o histórico textual vive em EVOLUCAO.
   Alternativa considerada: tabela `SINAL_VITAL` separada, versionando cada triagem — descartada por não ser necessária nesta fase (não implementada no protótipo) e por adicionar complexidade sem requisito que a justifique.

4. **RBAC por perfil (enfermeiro/médico) definido no cadastro do colaborador**, sem seleção manual em produção — o seletor "Perfil (demonstração)" do protótipo é explicitamente um atalho de demo, não uma decisão de produto.

## Risks / Trade-offs

- [Risco] Sem MFA, matrícula+PIN de 4 dígitos é um segredo fraco (10.000 combinações) → Mitigação: bloqueio por tentativas (rate limiting) a definir na implementação real; reavaliar MFA antes de produção.
- [Risco] Sem entidade de histórico de sinais vitais, perde-se a granularidade de triagens repetidas do mesmo paciente → Mitigação: aceitável nesta fase (um atendimento por visita, conforme protótipo); reavaliar se houver requisito de reavaliação clínica.
- [Risco] Specs geradas a partir de docs/protótipo já escritos podem divergir do SRD se este for editado depois sem sincronizar → Mitigação: `02-requisitos.md`/`03-casos-uso.md` seguem como fonte legível para humanos; specs em `openspec/specs/` são a fonte executável/testável — rodar `openspec sync` quando o SRD mudar.

## Migration Plan

Não há dado em produção a migrar (nenhuma implementação real existe). Ao implementar o back-end, seguir `tasks.md` desta mudança; as specs entram em `openspec/specs/` na arquivação (archive) desta change.

## Open Questions

- Formato exato do rate limiting/bloqueio de tentativas de PIN (quantas tentativas, janela de tempo) — a definir na implementação.
- Tempo de expiração de sessão/JWT — mencionado em `06-arquitetura.md` como "a definir na implementação".
