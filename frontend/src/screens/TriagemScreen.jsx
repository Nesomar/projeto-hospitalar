import { useEffect, useState } from "react";
import { ACENTO, COLORS } from "../colors.js";
import { calcularTriagem, confirmarTriagem, listarPainel } from "../api.js";

function defaultForm() {
  return { pas: "", pad: "", fc: "", fr: "", temp: "", spo2: "", dor: 0, queixa: "" };
}

const NUM_FIELDS = [
  { key: "pas", label: "PA sistólica", placeholder: "120" },
  { key: "pad", label: "PA diastólica", placeholder: "80" },
  { key: "fc", label: "FC (bpm)", placeholder: "80" },
  { key: "fr", label: "FR (irpm)", placeholder: "16" },
  { key: "temp", label: "Temperatura (°C)", placeholder: "36.5" },
  { key: "spo2", label: "SpO2 (%)", placeholder: "97" },
];

export default function TriagemScreen({ token, showToast, pacienteId, onSelecionarPaciente, onCancelar, onConfirmado }) {
  const [pendentes, setPendentes] = useState([]);
  const [carregandoLista, setCarregandoLista] = useState(true);
  const [form, setForm] = useState(defaultForm());
  const [resultado, setResultado] = useState(null);

  useEffect(() => {
    if (pacienteId) return;
    let cancelado = false;
    listarPainel(token)
      .then((dados) => {
        if (!cancelado) setPendentes(dados.filter((p) => p.status === "Aguardando Triagem"));
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

  function update(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function onCalcular() {
    if (!form.pas || !form.fc || !form.temp || !form.spo2) {
      showToast("Preencha PA, FC, Temperatura e SpO2 para calcular.");
      return;
    }
    try {
      const dados = await calcularTriagem(token, {
        pas: Number(form.pas),
        pad: form.pad ? Number(form.pad) : undefined,
        fc: Number(form.fc),
        fr: form.fr ? Number(form.fr) : undefined,
        temp: Number(form.temp),
        spo2: Number(form.spo2),
        dor: Number(form.dor),
      });
      setResultado(dados);
    } catch (err) {
      showToast(err.message || "Erro ao calcular classificação.");
    }
  }

  async function onConfirmar() {
    if (!resultado) return;
    try {
      await confirmarTriagem(token, pacienteId, {
        pas: Number(form.pas),
        pad: form.pad ? Number(form.pad) : undefined,
        fc: Number(form.fc),
        fr: form.fr ? Number(form.fr) : undefined,
        temp: Number(form.temp),
        spo2: Number(form.spo2),
        dor: Number(form.dor),
        queixa: form.queixa || undefined,
      });
      showToast(`Triagem confirmada: classificação ${COLORS[resultado.cor].label}.`);
      setForm(defaultForm());
      setResultado(null);
      onConfirmado();
    } catch (err) {
      showToast(err.message || "Erro ao confirmar triagem.");
    }
  }

  if (!pacienteId) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ fontSize: 14, color: "oklch(50% 0.018 258)" }}>Selecione um paciente aguardando triagem:</div>
        {carregandoLista && <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>}
        {!carregandoLista &&
          pendentes.map((p) => (
            <div
              key={p.paciente_id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                background: "#fff",
                border: "1px solid oklch(90% 0.012 258)",
                borderRadius: 14,
                padding: "16px 20px",
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14.5, fontWeight: 700 }}>{p.nome}</div>
              </div>
              <button
                onClick={() => onSelecionarPaciente(p.paciente_id)}
                style={{ border: "none", background: ACENTO, color: "#fff", padding: "9px 16px", borderRadius: 10, fontSize: 13, fontWeight: 700, cursor: "pointer" }}
              >
                Selecionar
              </button>
            </div>
          ))}
        {!carregandoLista && pendentes.length === 0 && (
          <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)", fontSize: 14 }}>
            Nenhum paciente aguardando triagem.
          </div>
        )}
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
        <div style={{ display: "flex", gap: 14 }}>
          {NUM_FIELDS.slice(0, 3).map((campo) => (
            <div key={campo.key} style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 12, fontWeight: 700 }}>{campo.label}</label>
              <input
                type="number"
                value={form[campo.key]}
                onChange={(e) => update(campo.key, e.target.value)}
                placeholder={campo.placeholder}
                style={{ width: "100%", border: "1px solid oklch(88% 0.012 258)", borderRadius: 10, padding: "9px 10px", fontSize: 13, boxSizing: "border-box" }}
              />
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 14 }}>
          {NUM_FIELDS.slice(3).map((campo) => (
            <div key={campo.key} style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 12, fontWeight: 700 }}>{campo.label}</label>
              <input
                type="number"
                value={form[campo.key]}
                onChange={(e) => update(campo.key, e.target.value)}
                placeholder={campo.placeholder}
                style={{ width: "100%", border: "1px solid oklch(88% 0.012 258)", borderRadius: 10, padding: "9px 10px", fontSize: 13, boxSizing: "border-box" }}
              />
            </div>
          ))}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <label style={{ fontSize: 12, fontWeight: 700 }}>Dor (0-10)</label>
          <input type="range" min="0" max="10" value={form.dor} onChange={(e) => update("dor", e.target.value)} style={{ width: "100%" }} />
          <div style={{ fontSize: 12, color: "oklch(50% 0.018 258)" }}>Nível: {form.dor}</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <label style={{ fontSize: 12, fontWeight: 700 }}>Queixa principal</label>
          <textarea
            value={form.queixa}
            onChange={(e) => update("queixa", e.target.value)}
            placeholder="Descreva a queixa..."
            style={{ border: "1px solid oklch(88% 0.012 258)", borderRadius: 12, padding: "11px 14px", fontSize: 13, minHeight: 70, resize: "vertical", boxSizing: "border-box" }}
          />
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
          <button
            onClick={onCalcular}
            style={{ border: "none", background: ACENTO, color: "#fff", padding: "11px 18px", borderRadius: 12, fontSize: 13.5, fontWeight: 700, cursor: "pointer" }}
          >
            Calcular Classificação
          </button>
          <button
            onClick={onCancelar}
            style={{ border: "1px solid oklch(88% 0.012 258)", background: "#fff", padding: "11px 18px", borderRadius: 12, fontSize: 13.5, fontWeight: 700, color: "oklch(40% 0.02 258)", cursor: "pointer" }}
          >
            Cancelar
          </button>
        </div>
      </div>
      <div style={{ flex: "1 1 260px", minWidth: 260, maxWidth: 340, display: "flex", flexDirection: "column", gap: 14 }}>
        {resultado ? (
          <>
            <div
              style={{
                background: COLORS[resultado.cor].bg,
                color: COLORS[resultado.cor].text,
                borderRadius: 16,
                padding: 20,
                boxSizing: "border-box",
              }}
            >
              <div style={{ fontSize: 13, fontWeight: 700, opacity: 0.85 }}>Classificação de Risco</div>
              <div style={{ fontSize: 22, fontWeight: 800, marginTop: 4 }}>{COLORS[resultado.cor].label}</div>
              <div style={{ fontSize: 13, marginTop: 2 }}>Meta de atendimento: {resultado.tempo_meta}</div>
              <div style={{ fontSize: 12.5, marginTop: 10, opacity: 0.9, lineHeight: 1.5 }}>{resultado.justificativa}</div>
            </div>
            <button
              onClick={onConfirmar}
              style={{ border: "none", background: ACENTO, color: "#fff", padding: 13, borderRadius: 12, fontSize: 14, fontWeight: 700, cursor: "pointer" }}
            >
              Confirmar Triagem
            </button>
          </>
        ) : (
          <div style={{ background: "oklch(96% 0.008 258)", borderRadius: 16, padding: 20, fontSize: 13, color: "oklch(50% 0.018 258)", lineHeight: 1.6, boxSizing: "border-box" }}>
            Preencha os sinais vitais e clique em "Calcular Classificação" para obter a cor de risco segundo o Protocolo de Manchester.
          </div>
        )}
      </div>
    </div>
  );
}
