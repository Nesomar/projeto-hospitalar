import { useCallback, useEffect, useState } from "react";
import { COLORS, ACENTO } from "../colors.js";
import { darAlta, listarPainel, retomarAtendimento, solicitarExames } from "../api.js";
import ConfirmModal from "../components/ConfirmModal.jsx";

const FILTROS = [{ key: "todos", label: "Todos" }, ...Object.keys(COLORS).map((c) => ({ key: c, label: COLORS[c].label }))];

const ACAO_CONFIG = {
  alta: {
    title: "Confirmar Alta",
    description: (nome) => `Confirma a alta do paciente ${nome}?`,
    confirmLabel: "Confirmar Alta",
    showObservacoes: false,
    executar: (token, id) => darAlta(token, id),
    mensagemSucesso: "Alta registrada.",
  },
  exames: {
    title: "Solicitar Exames Complementares",
    description: (nome) => `Solicitar exames complementares para ${nome}.`,
    confirmLabel: "Solicitar Exames",
    showObservacoes: true,
    executar: (token, id, observacoes) => solicitarExames(token, id, observacoes),
    mensagemSucesso: "Exames complementares solicitados.",
  },
  retomar: {
    title: "Retomar Atendimento",
    description: (nome) => `Confirma a retomada do atendimento de ${nome} após exames complementares?`,
    confirmLabel: "Retomar Atendimento",
    showObservacoes: false,
    executar: (token, id) => retomarAtendimento(token, id),
    mensagemSucesso: "Atendimento retomado.",
  },
};

export default function PainelScreen({ token, showToast, onAbrirTriagem, onAbrirProntuario, onAbrirIniciarAtendimento }) {
  const [filtroCor, setFiltroCor] = useState("todos");
  const [pacientes, setPacientes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [acaoModal, setAcaoModal] = useState(null);

  const carregar = useCallback(() => {
    setCarregando(true);
    return listarPainel(token, filtroCor === "todos" ? undefined : filtroCor)
      .then((dados) => setPacientes(dados))
      .catch((err) => showToast(err.message || "Erro ao carregar painel."))
      .finally(() => setCarregando(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroCor, token]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function onConfirmarAcao(observacoes) {
    const { tipo, paciente } = acaoModal;
    const config = ACAO_CONFIG[tipo];
    try {
      await config.executar(token, paciente.paciente_id, observacoes);
      showToast(config.mensagemSucesso);
      setAcaoModal(null);
    } catch (err) {
      showToast(err.message || "Erro ao executar ação.");
      setAcaoModal(null);
    } finally {
      carregar();
    }
  }

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
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
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
                  {p.pode_iniciar_atendimento && (
                    <button
                      onClick={() => onAbrirIniciarAtendimento(p.paciente_id)}
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
                      Iniciar Atendimento
                    </button>
                  )}
                  {p.pode_solicitar_exames && (
                    <button
                      onClick={() => setAcaoModal({ tipo: "exames", paciente: p })}
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
                      Solicitar Exames
                    </button>
                  )}
                  {p.pode_dar_alta && (
                    <button
                      onClick={() => setAcaoModal({ tipo: "alta", paciente: p })}
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
                      Dar Alta
                    </button>
                  )}
                  {p.pode_retomar_atendimento && (
                    <button
                      onClick={() => setAcaoModal({ tipo: "retomar", paciente: p })}
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
                      Retomar Atendimento
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

      {acaoModal && (
        <ConfirmModal
          title={ACAO_CONFIG[acaoModal.tipo].title}
          description={ACAO_CONFIG[acaoModal.tipo].description(acaoModal.paciente.nome)}
          confirmLabel={ACAO_CONFIG[acaoModal.tipo].confirmLabel}
          showObservacoes={ACAO_CONFIG[acaoModal.tipo].showObservacoes}
          onConfirm={onConfirmarAcao}
          onCancel={() => setAcaoModal(null)}
        />
      )}
    </div>
  );
}
