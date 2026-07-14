import { useEffect, useState } from "react";
import { ACENTO, COLORS } from "../colors.js";
import { consultarProntuario, listarPainel } from "../api.js";

const VITAL_LABELS = {
  pas: "PA sist.",
  pad: "PA diast.",
  fc: "FC",
  fr: "FR",
  temp: "Temp.",
  spo2: "SpO2",
  dor: "Dor",
};

export default function ProntuarioScreen({ token, showToast, pacienteId, onSelecionarPaciente, onNovaPrescricao, onVoltarPainel }) {
  const [pacientes, setPacientes] = useState([]);
  const [carregandoLista, setCarregandoLista] = useState(true);
  const [prontuario, setProntuario] = useState(null);
  const [carregandoProntuario, setCarregandoProntuario] = useState(false);

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
    let cancelado = false;
    setCarregandoProntuario(true);
    consultarProntuario(token, pacienteId)
      .then((dados) => {
        if (!cancelado) setProntuario(dados);
      })
      .catch((err) => showToast(err.message || "Erro ao carregar prontuário."))
      .finally(() => {
        if (!cancelado) setCarregandoProntuario(false);
      });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pacienteId, token]);

  if (!pacienteId) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ fontSize: 14, color: "oklch(50% 0.018 258)" }}>Selecione um paciente:</div>
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
                  Abrir
                </button>
              </div>
            );
          })}
      </div>
    );
  }

  if (carregandoProntuario || !prontuario) {
    return <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>;
  }

  const classInfo = prontuario.sinais_vitais.classificacao_risco
    ? COLORS[prontuario.sinais_vitais.classificacao_risco]
    : { bg: "oklch(92% 0.008 258)", text: "oklch(45% 0.015 258)" };
  const classLabel = prontuario.sinais_vitais.classificacao_risco
    ? COLORS[prontuario.sinais_vitais.classificacao_risco].label
    : "Não classificado";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 20, padding: "24px 28px", boxSizing: "border-box" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ fontSize: 19, fontWeight: 800 }}>{prontuario.paciente_nome}</div>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: classInfo.bg, color: classInfo.text, fontSize: 12, fontWeight: 700 }}>
            {classLabel}
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))", gap: 12, marginTop: 20 }}>
          {Object.entries(VITAL_LABELS).map(([campo, label]) => (
            <div key={campo} style={{ background: "oklch(97% 0.006 258)", borderRadius: 12, padding: "10px 12px" }}>
              <div style={{ fontSize: 10.5, color: "oklch(55% 0.015 258)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.03em" }}>{label}</div>
              <div style={{ fontSize: 16, fontWeight: 800, marginTop: 2 }}>{prontuario.sinais_vitais[campo] ?? "—"}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 20, padding: "24px 28px", boxSizing: "border-box" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 14 }}>Evolução</div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          {prontuario.evolucoes.map((e) => (
            <div key={e.id} style={{ display: "flex", gap: 14, paddingBottom: 18, borderLeft: "2px solid oklch(90% 0.012 258)", marginLeft: 4, paddingLeft: 18, position: "relative" }}>
              <div style={{ position: "absolute", left: -6, top: 2, width: 10, height: 10, borderRadius: "50%", background: ACENTO }} />
              <div>
                <div style={{ fontSize: 12, color: "oklch(50% 0.018 258)" }}>
                  {new Date(e.data).toLocaleString("pt-BR")} · {e.responsavel_matricula}
                </div>
                <div style={{ fontSize: 11.5, fontWeight: 700, color: "oklch(45% 0.02 258)", marginTop: 2 }}>{e.tipo}</div>
                <div style={{ fontSize: 13, marginTop: 4, lineHeight: 1.5 }}>{e.descricao}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 20, padding: "24px 28px", boxSizing: "border-box" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div style={{ fontSize: 14, fontWeight: 700 }}>Prescrições</div>
          {prontuario.pode_prescrever && (
            <button
              onClick={() => onNovaPrescricao(pacienteId)}
              style={{ border: "none", background: ACENTO, color: "#fff", padding: "9px 16px", borderRadius: 10, fontSize: 12.5, fontWeight: 700, cursor: "pointer" }}
            >
              + Nova Prescrição
            </button>
          )}
        </div>
        {prontuario.prescricoes.map((rx) => (
          <div key={rx.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderTop: "1px solid oklch(94% 0.008 258)" }}>
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 700 }}>
                {rx.medicamento} — {rx.dosagem}
              </div>
              <div style={{ fontSize: 12, color: "oklch(50% 0.018 258)", marginTop: 2 }}>
                {rx.via} · {rx.frequencia || "—"} · {new Date(rx.data).toLocaleString("pt-BR")} · {rx.responsavel_matricula}
              </div>
            </div>
          </div>
        ))}
        {prontuario.prescricoes.length === 0 && (
          <div style={{ fontSize: 13, color: "oklch(55% 0.015 258)", padding: "8px 0" }}>Nenhuma prescrição registrada.</div>
        )}
      </div>

      <button
        onClick={onVoltarPainel}
        style={{ alignSelf: "flex-start", border: "1px solid oklch(88% 0.012 258)", background: "#fff", padding: "10px 18px", borderRadius: 12, fontSize: 13, fontWeight: 700, color: "oklch(40% 0.02 258)", cursor: "pointer" }}
      >
        ← Voltar ao Painel
      </button>
    </div>
  );
}
