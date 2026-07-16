const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

let onUnauthorized = null;

export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

function extractMessage(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  return "Erro inesperado.";
}

async function request(path, { method = "GET", body, token, params } = {}) {
  const url = new URL(BASE_URL + path);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
    });
  }

  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const resp = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!resp.ok) {
    const payload = await resp.json().catch(() => null);
    if (resp.status === 401 && token) onUnauthorized?.();
    throw new ApiError(extractMessage(payload?.detail), resp.status);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

export function login(matricula, pin) {
  return request("/api/auth/login", { method: "POST", body: { matricula, pin } });
}

export function listarPainel(token, cor) {
  return request("/api/painel", { token, params: { cor } });
}

export function cadastrarPaciente(token, dados) {
  return request("/api/pacientes", { method: "POST", token, body: dados });
}

export function calcularTriagem(token, sinaisVitais) {
  return request("/api/triagem/calcular", { method: "POST", token, body: sinaisVitais });
}

export function confirmarTriagem(token, pacienteId, dados) {
  return request(`/api/pacientes/${pacienteId}/triagem/confirmar`, {
    method: "POST",
    token,
    body: dados,
  });
}

export function consultarProntuario(token, pacienteId) {
  return request(`/api/pacientes/${pacienteId}/prontuario`, { token });
}

export function prescrever(token, pacienteId, dados) {
  return request(`/api/pacientes/${pacienteId}/prescricoes`, {
    method: "POST",
    token,
    body: dados,
  });
}

export function iniciarAtendimento(token, pacienteId) {
  return request(`/api/pacientes/${pacienteId}/atendimento/iniciar`, { method: "POST", token });
}

export function darAlta(token, pacienteId) {
  return request(`/api/pacientes/${pacienteId}/atendimento/alta`, { method: "POST", token });
}

export function solicitarExames(token, pacienteId, observacoes) {
  return request(`/api/pacientes/${pacienteId}/atendimento/exames`, {
    method: "POST",
    token,
    body: { observacoes: observacoes || undefined },
  });
}

export function retomarAtendimento(token, pacienteId) {
  return request(`/api/pacientes/${pacienteId}/atendimento/retomar`, { method: "POST", token });
}

export function cadastrarColaborador(token, dados) {
  return request("/api/colaboradores", { method: "POST", token, body: dados });
}
