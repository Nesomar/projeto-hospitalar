# Documento de Visão

## 1. Problema e Oportunidade
* **O Problema**: O cadastro de pacientes, o registro de triagem e o acompanhamento do prontuário na UPA Nordeste são feitos de forma manual (papel/planilhas), sem padronização da classificação de risco.
* **Impacto**: Tempo elevado para cadastrar pacientes e localizar prontuários; risco de erro na priorização de atendimento por falta de um protocolo de triagem padronizado e auditável; dificuldade de rastrear evolução clínica e prescrições ao longo do atendimento.
* **Solução Proposta**: Sistema informatizado que automatiza o cadastro de pacientes (CPF/CNS), a triagem por classificação de risco (Protocolo de Manchester), a consulta de prontuário eletrônico e o registro de prescrições, com autenticação de colaborador (matrícula + PIN) e trilha de auditoria por evolução clínica.

## 2. Partes Interessadas (Stakeholders)
* **Enfermeiros(as)**: realizam cadastro de pacientes e triagem (classificação de risco).
* **Médicos(as)**: consultam prontuário e registram prescrições.
* **Pacientes**: beneficiários do atendimento; seus dados são protegidos por LGPD.
* **Gestão hospitalar / Direção da UPA Nordeste**: patrocinadora, interessada em tempo de atendimento e conformidade.
* **Centro de Informática UFPE**: responsável técnico pela implementação e manutenção do sistema.

## 3. Escopo do Produto
**Incluído nesta fase:**
* Autenticação de colaboradores (matrícula + PIN).
* Cadastro de pacientes (dados pessoais, CPF, CNS).
* Triagem com cálculo automático da classificação de risco (Protocolo de Manchester: Vermelho, Laranja, Amarelo, Verde, Azul).
* Painel de atendimento com fila ordenada por gravidade.
* Prontuário eletrônico (sinais vitais, evolução clínica, histórico).
* Registro de prescrições médicas.

**Fora de escopo nesta fase:**
* Integração real com AGHU/HIS legado (ver `05-interfaces.md`).
* Faturamento e integração TISS/convênios.
* Agendamento de exames e emissão de laudos.

## 4. Metas e Objetivos de Negócio
* Reduzir o tempo de cadastro e de localização do prontuário do paciente frente ao processo manual atual.
* Garantir que 100% das triagens sigam o Protocolo de Manchester, com classificação de risco e justificativa registradas.
* Eliminar perda ou extravio de registros de evolução clínica e prescrições (trilha de auditoria imutável, sem exclusão física — ver `06-arquitetura.md`).
* Assegurar conformidade com a LGPD no tratamento de dados sensíveis de saúde.
