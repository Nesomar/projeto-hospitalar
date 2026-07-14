export const COLORS = {
  vermelho: { bg: "#D62839", text: "#ffffff", label: "Vermelho", tempo: "Imediato" },
  laranja: { bg: "#F07D12", text: "#ffffff", label: "Laranja", tempo: "Até 10 min" },
  amarelo: { bg: "#F0C808", text: "#3A2E00", label: "Amarelo", tempo: "Até 60 min" },
  verde: { bg: "#2E9E4F", text: "#ffffff", label: "Verde", tempo: "Até 120 min" },
  azul: { bg: "#1E73BE", text: "#ffffff", label: "Azul", tempo: "Até 240 min" },
};

export const ACENTO = "#2F6FED";

export function formatCPF(cpf) {
  if (!cpf) return "";
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

export function formatCNS(cns) {
  if (!cns) return "";
  return cns.replace(/(\d{3})(\d{4})(\d{4})(\d{4})/, "$1 $2 $3 $4");
}

export function calcIdade(dataStr) {
  if (!dataStr) return "";
  const nasc = new Date(dataStr + "T00:00:00");
  const hoje = new Date();
  let idade = hoje.getFullYear() - nasc.getFullYear();
  const m = hoje.getMonth() - nasc.getMonth();
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
  return idade;
}
