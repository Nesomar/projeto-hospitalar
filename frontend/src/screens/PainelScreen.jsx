import { useEffect, useState } from "react";
import { COLORS, ACENTO } from "../colors.js";
import { listarPainel } from "../api.js";

const FILTROS = [{ key: "todos", label: "Todos" }, ...Object.keys(COLORS).map((c) => ({ key: c, label: COLORS[c].label }))];

export default function PainelScreen({ token, showToast, onAbrirTriagem, onAbrirProntuario }) {
  const [filtroCor, setFiltroCor] = useState("todos");
  const [pacientes, setPacientes] = useState([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let cancelado = false;
    setCarregando(true);
    listarPainel(token, filtroCor === "todos" ? undefined : filtroCor)
      .then((dados) => {
        if (!cancelado) setPacientes(dados);
      })
      .catch((err) => showToast(err.message || "Erro ao carregar painel."))
      .finally(() => {
        if (!cancelado) setCarregando(false);
      });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroCor, token]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {FILTROS.map((f) => {
          const active = filtroCor === f.key;
          const baseColor = f.key === "todos" ? ACENTO : COLORS[f.key].bg;
          return (
            <button
              key={f.key}
              onClick={() => setFiltroCor(f.key)}
              style={{
                border: active ? "1px solid transparent" : "1px solid oklch(88% 0.012 258)",
                background: active ? baseColor : "#ffffff",
                color: active ? "#ffffff" : "oklch(40% 0.02 258)",
                padding: "8px 16px",
                borderRadius: 999,
                fontSize: 12.5,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {carregando && <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>}
        {!carregando &&
          pacientes.map((p) => {
            const classInfo = p.classificacao_risco
              ? COLORS[p.classificacao_risco]
              : { bg: "oklch(92% 0.008 258)", text: "oklch(45% 0.015 258)" };
            return (
              <div
                key={p.paciente_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  background: "#ffffff",
                  border: "1px solid oklch(90% 0.012 258)",
                  borderLeft: `5px solid ${classInfo.bg}`,
                  borderRadius: 14,
                  padding: "14px 20px",
                }}
              >
                <div
                  style={{
                    width: 74,
                    textAlign: "center",
                    padding: "6px 0",
                    borderRadius: 10,
                    background: classInfo.bg,
                    color: classInfo.text,
                    fontSize: 11.5,
                    fontWeight: 800,
                    flexShrink: 0,
                  }}
                >
                  {p.classificacao_risco ? COLORS[p.classificacao_risco].label : "—"}
                </div>
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
                  <div style={{ fontSize: 15, fontWeight: 700 }}>{p.nome}</div>
                </div>
                <div
                  style={{
                    fontSize: 11.5,
                    fontWeight: 700,
                    color: "oklch(45% 0.018 258)",
                    background: "oklch(96% 0.008 258)",
                    padding: "6px 12px",
                    borderRadius: 999,
                    whiteSpace: "nowrap",
                  }}
                >
                  {p.status}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  {p.pode_fazer_triagem && (
                    <button
                      onClick={() => onAbrirTriagem(p.paciente_id)}
                      style={{
                        border: "none",
                        background: ACENTO,
                        color: "#fff",
                        padding: "9px 14px",
                        borderRadius: 10,
                        fontSize: 12.5,
                        fontWeight: 700,
                        cursor: "pointer",
                        whiteSpace: "nowrap",
                      }}
                    >
                      Fazer Triagem
                    </button>
                  )}
                  <button
                    onClick={() => onAbrirProntuario(p.paciente_id)}
                    style={{
                      border: "1px solid oklch(88% 0.012 258)",
                      background: "#fff",
                      padding: "9px 14px",
                      borderRadius: 10,
                      fontSize: 12.5,
                      fontWeight: 700,
                      color: "oklch(40% 0.02 258)",
                      cursor: "pointer",
                      whiteSpace: "nowrap",
                    }}
                  >
                    Ver Prontuário
                  </button>
                </div>
              </div>
            );
          })}
        {!carregando && pacientes.length === 0 && (
          <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)", fontSize: 14 }}>
            Nenhum paciente nesta classificação.
          </div>
        )}
      </div>

      <div style={{ marginTop: 8, padding: "18px 20px", background: "#ffffff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10 }}>Protocolo de Manchester</div>
        <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
          {Object.entries(COLORS).map(([cor, info]) => (
            <div key={cor} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "oklch(45% 0.018 258)" }}>
              <span style={{ width: 10, height: 10, borderRadius: "50%", background: info.bg, display: "inline-block" }} />
              {info.label} · {info.tempo}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
