import { useState } from "react";
import { s } from "../styles.js";
import { ACENTO } from "../colors.js";
import { login } from "../api.js";

export default function LoginScreen({ onLoginSuccess, showToast }) {
  const [matricula, setMatricula] = useState("");
  const [pin, setPin] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    if (enviando) return;
    setEnviando(true);
    try {
      const { access_token } = await login(matricula, pin);
      onLoginSuccess(access_token);
    } catch (err) {
      showToast(err.message || "Matrícula ou PIN inválidos.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <form
        onSubmit={onSubmit}
        style={{
          width: 400,
          background: "#ffffff",
          borderRadius: 24,
          padding: "40px 36px",
          boxShadow: "0 20px 50px -20px oklch(20% 0.02 258 / 0.18)",
          display: "flex",
          flexDirection: "column",
          gap: 20,
          boxSizing: "border-box",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, textAlign: "center" }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: ACENTO,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 800,
              fontSize: 20,
            }}
          >
            UN
          </div>
          <div>
            <div style={{ fontSize: 19, fontWeight: 800 }}>UPA Nordeste</div>
            <div style={{ fontSize: 13, color: "oklch(50% 0.018 258)", marginTop: 2 }}>
              Hospital das Clínicas · Sistema de Atendimento
            </div>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={s.field}>
            <label style={s.label}>Matrícula</label>
            <input
              type="text"
              value={matricula}
              onChange={(e) => setMatricula(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="ex: 000123"
              inputMode="numeric"
              style={s.input}
            />
          </div>
          <div style={s.field}>
            <label style={s.label}>PIN</label>
            <input
              type="password"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
              placeholder="••••"
              inputMode="numeric"
              style={s.input}
            />
          </div>
          <button type="submit" disabled={enviando} style={{ ...s.btnPrimary, marginTop: 6 }}>
            {enviando ? "Entrando..." : "Entrar"}
          </button>
        </div>
        <div style={{ textAlign: "center", fontSize: 11, color: "oklch(58% 0.015 258)" }}>
          Autenticação por matrícula e PIN institucional (RF001).
        </div>
      </form>
    </div>
  );
}
