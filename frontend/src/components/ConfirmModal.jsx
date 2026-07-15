import { useState } from "react";
import { ACENTO } from "../colors.js";

export default function ConfirmModal({ title, description, confirmLabel = "Confirmar", showObservacoes = false, onConfirm, onCancel }) {
  const [observacoes, setObservacoes] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function handleConfirm() {
    setEnviando(true);
    try {
      await onConfirm(showObservacoes ? observacoes || undefined : undefined);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "oklch(20% 0.02 258 / 0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 20,
          padding: "26px 28px",
          width: 380,
          maxWidth: "90vw",
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        <div style={{ fontSize: 16, fontWeight: 800 }}>{title}</div>
        <div style={{ fontSize: 13, color: "oklch(50% 0.018 258)", lineHeight: 1.5 }}>{description}</div>
        {showObservacoes && (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <label style={{ fontSize: 12, fontWeight: 700 }}>Observações (opcional)</label>
            <textarea
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Descreva os exames solicitados..."
              style={{
                border: "1px solid oklch(88% 0.012 258)",
                borderRadius: 12,
                padding: "11px 14px",
                fontSize: 13,
                minHeight: 70,
                resize: "vertical",
                boxSizing: "border-box",
              }}
            />
          </div>
        )}
        <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
          <button
            onClick={handleConfirm}
            disabled={enviando}
            style={{
              border: "none",
              background: ACENTO,
              color: "#fff",
              padding: "11px 18px",
              borderRadius: 12,
              fontSize: 13.5,
              fontWeight: 700,
              cursor: enviando ? "default" : "pointer",
              opacity: enviando ? 0.7 : 1,
            }}
          >
            {enviando ? "Enviando..." : confirmLabel}
          </button>
          <button
            onClick={onCancel}
            disabled={enviando}
            style={{
              border: "1px solid oklch(88% 0.012 258)",
              background: "#fff",
              padding: "11px 18px",
              borderRadius: 12,
              fontSize: 13.5,
              fontWeight: 700,
              color: "oklch(40% 0.02 258)",
              cursor: "pointer",
            }}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
