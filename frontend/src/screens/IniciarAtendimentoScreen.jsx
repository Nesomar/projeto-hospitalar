import { useEffect, useState } from "react";
import { ACENTO, COLORS } from "../colors.js";
import { consultarProntuario, iniciarAtendimento, listarPainel } from "../api.js";

export default function IniciarAtendimentoScreen({ token, showToast, pacienteId, onSelecionarPaciente, onCancelar, onConfirmado }) {
  const [pendentes, setPendentes] = useState([]);
  const [carregandoLista, setCarregandoLista] = useState(true);
  const [prontuario, setProntuario] = useState(null);
  const [carregandoProntuario, setCarregandoProntuario] = useState(false);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (pacienteId) return;
    let cancelado = false;
    listarPainel(token)
      .then((dados) => {
        if (!cancelado) setPendentes(dados.filter((p) => p.pode_iniciar_atendimento));
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

  async function onConfirmar() {
    setEnviando(true);
    try {
      await iniciarAtendimento(token, pacienteId);
      showToast("Atendimento iniciado.");
      onConfirmado();
    } catch (err) {
      showToast(err.message || "Erro ao iniciar atendimento.");
    } finally {
      setEnviando(false);
    }
  }

  if (!pacienteId) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ fontSize: 14, color: "oklch(50% 0.018 258)" }}>Selecione um paciente aguardando atendimento:</div>
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
            Nenhum paciente aguardando atendimento.
          </div>
        )}
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
    <div style={{ maxWidth: 480, display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ background: "#fff", border: "1px solid oklch(90% 0.012 258)", borderRadius: 20, padding: "24px 28px", boxSizing: "border-box" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ fontSize: 19, fontWeight: 800 }}>{prontuario.paciente_nome}</div>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: classInfo.bg, color: classInfo.text, fontSize: 12, fontWeight: 700 }}>
            {classLabel}
          </div>
        </div>
      </div>
      <div style={{ display: "flex", gap: 10 }}>
        <button
          onClick={onConfirmar}
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
          {enviando ? "Iniciando..." : "Iniciar Atendimento"}
        </button>
        <button
          onClick={onCancelar}
          style={{ border: "1px solid oklch(88% 0.012 258)", background: "#fff", padding: "11px 18px", borderRadius: 12, fontSize: 13.5, fontWeight: 700, color: "oklch(40% 0.02 258)", cursor: "pointer" }}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
