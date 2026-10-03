import { useEffect, useState } from "react";
import { COLORS } from "../colors.js";
import { consultarProntuario, listarPainel } from "../api.js";
import PrescricaoForm from "../components/PrescricaoForm.jsx";

export default function PrescricaoScreen({ token, matricula, showToast, pacienteId, onSelecionarPaciente, onPrescrito }) {
  const [pacientes, setPacientes] = useState([]);
  const [carregandoLista, setCarregandoLista] = useState(true);
  const [prontuario, setProntuario] = useState(null);

  useEffect(() => {
    if (pacienteId) return;
    let cancelado = false;
    listarPainel(token)
      .then((dados) => {
        if (!cancelado) setPacientes(dados);
      })
      .catch((err) => showToast(err.message || "Erro ao carregar pacientes."))
      .finally(() => {
        if (!cancelado) setCarregandoLista(false);
      });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pacienteId, token]);

  useEffect(() => {
    if (!pacienteId) return;
    consultarProntuario(token, pacienteId)
      .then(setProntuario)
      .catch((err) => showToast(err.message || "Erro ao carregar prontuário."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pacienteId, token]);

  if (!pacienteId) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ fontSize: 14, color: "oklch(50% 0.018 258)" }}>Selecione um paciente para prescrever:</div>
        {carregandoLista && <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>}
        {!carregandoLista &&
          pacientes.map((p) => {
            const dotColor = p.classificacao_risco ? COLORS[p.classificacao_risco].bg : "oklch(85% 0.01 258)";
            return (
              <div
                key={p.paciente_id}
                style={{ display: "flex", alignItems: "center", gap: 16, background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 14, padding: "14px 20px" }}
              >
                <div style={{ width: 10, height: 10, borderRadius: "50%", background: dotColor, flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{p.nome}</div>
                  <div style={{ fontSize: 12, color: "oklch(50% 0.018 258)" }}>{p.status}</div>
                </div>
                <button
                  onClick={() => onSelecionarPaciente(p.paciente_id)}
                  style={{ border: "1px solid oklch(88% 0.012 258)", background: "#fff", padding: "8px 14px", borderRadius: 10, fontSize: 12.5, fontWeight: 700, cursor: "pointer" }}
                >
                  Selecionar
                </button>
              </div>
            );
          })}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 24, alignItems: "flex-start" }}>
      <div
        style={{
          flex: "2 1 380px",
          maxWidth: 520,
          minWidth: 0,
          background: "#fff",
          border: "1px solid oklch(90% 0.012 258)",
          borderRadius: 20,
          padding: "26px 30px",
          display: "flex",
          flexDirection: "column",
          gap: 14,
          boxSizing: "border-box",
        }}
      >
        <div>
          <div style={{ fontSize: 16, fontWeight: 800 }}>{prontuario?.paciente_nome}</div>
          <div style={{ fontSize: 12, color: "oklch(50% 0.018 258)" }}>Prescrito por matrícula {matricula}</div>
        </div>
        <PrescricaoForm key={pacienteId} token={token} pacienteId={pacienteId} showToast={showToast} onPrescrito={onPrescrito} />
      </div>
      <div style={{ flex: "1 1 260px", minWidth: 260, maxWidth: 340, display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "oklch(45% 0.018 258)" }}>Prescrições anteriores</div>
        {(prontuario?.prescricoes || []).map((rx) => (
          <div key={rx.id} style={{ background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 14, padding: "14px 16px", boxSizing: "border-box" }}>
            <div style={{ fontSize: 13, fontWeight: 700 }}>
              {rx.medicamento} — {rx.dosagem}
            </div>
            <div style={{ fontSize: 11.5, color: "oklch(50% 0.018 258)", marginTop: 2 }}>
              {rx.via} · {rx.frequencia || "—"} · {new Date(rx.data).toLocaleString("pt-BR")}
            </div>
          </div>
        ))}
        {prontuario && prontuario.prescricoes.length === 0 && (
          <div style={{ fontSize: 12.5, color: "oklch(55% 0.015 258)" }}>Nenhuma prescrição anterior.</div>
        )}
      </div>
    </div>
  );
}
