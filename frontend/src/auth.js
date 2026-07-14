const STORAGE_KEY = "upa-nordeste-token";

export function decodeToken(token) {
  const payloadBase64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  const payload = JSON.parse(atob(payloadBase64));
  return { matricula: payload.sub, perfil: payload.perfil, exp: payload.exp };
}

export function salvarToken(token) {
  localStorage.setItem(STORAGE_KEY, token);
}

export function removerToken() {
  localStorage.removeItem(STORAGE_KEY);
}

export function carregarSessao() {
  const token = localStorage.getItem(STORAGE_KEY);
  if (!token) return null;
  try {
    const { matricula, perfil, exp } = decodeToken(token);
    if (exp * 1000 < Date.now()) {
      removerToken();
      return null;
    }
    return { token, matricula, perfil };
  } catch {
    removerToken();
    return null;
  }
}
