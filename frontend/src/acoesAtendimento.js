import { darAlta, iniciarAtendimento, retomarAtendimento, solicitarExames } from "./api.js";

export const ACAO_CONFIG = {
  iniciar: {
    title: "Iniciar Atendimento",
    description: (nome) => `Confirma o início do atendimento de ${nome}?`,
    confirmLabel: "Iniciar Atendimento",
    showObservacoes: false,
    executar: (token, id) => iniciarAtendimento(token, id),
    mensagemSucesso: "Atendimento iniciado.",
  },
  alta: {
    title: "Confirmar Alta",
    description: (nome) => `Confirma a alta do paciente ${nome}?`,
    confirmLabel: "Confirmar Alta",
    showObservacoes: false,
    executar: (token, id) => darAlta(token, id),
    mensagemSucesso: "Alta registrada.",
  },
  exames: {
    title: "Solicitar Exames Complementares",
    description: (nome) => `Solicitar exames complementares para ${nome}.`,
    confirmLabel: "Solicitar Exames",
    showObservacoes: true,
    executar: (token, id, observacoes) => solicitarExames(token, id, observacoes),
    mensagemSucesso: "Exames complementares solicitados.",
  },
  retomar: {
    title: "Retomar Atendimento",
    description: (nome) => `Confirma a retomada do atendimento de ${nome} após exames complementares?`,
    confirmLabel: "Retomar Atendimento",
    showObservacoes: false,
    executar: (token, id) => retomarAtendimento(token, id),
    mensagemSucesso: "Atendimento retomado.",
  },
};
