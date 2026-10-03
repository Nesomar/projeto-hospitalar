import { useCallback, useEffect, useRef, useState } from "react";
import { ACENTO, COLORS, calcIdade, formatCNS, formatCPF } from "../colors.js";
import { consultarProntuario, listarPainel } from "../api.js";
import { ACAO_CONFIG } from "../acoesAtendimento.js";
import ConfirmModal from "../components/ConfirmModal.jsx";
import PrescricaoForm from "../components/PrescricaoForm.jsx";

const SEM_CLASSIFICACAO = { bg: "oklch(92% 0.008 258)", text: "oklch(45% 0.015 258)", label: "Não classificado" };
const SEXO_LABEL = { F: "Feminino", M: "Masculino", O: "Outro" };
const MUTED = "oklch(50% 0.018 258)";
const BORDA = "1px solid oklch(90% 0.012 258)";

const card = { background: "#fff", border: BORDA, borderRadius: 20, padding: "22px 26px", boxSizing: "border-box" };
const tituloSecao = { fontSize: 14, fontWeight: 700, margin: "0 0 14px" };
const btnPrimario = { border: "none", background: ACENTO, color: "#fff", padding: "11px 18px", borderRadius: 12, fontSize: 13.5, fontWeight: 700, cursor: "pointer", minHeight: 44 };
const btnSecundario = { border: "1px solid oklch(88% 0.012 258)", background: "#fff", padding: "11px 18px", borderRadius: 12, fontSize: 13.5, fontWeight: 700, color: "oklch(40% 0.02 258)", cursor: "pointer", minHeight: 44 };

// Ordem = ordem de exibição; a primeira ação disponível é a primária.
const ACOES = [
  { flag: "pode_iniciar_atendimento", tipo: "iniciar", label: "Iniciar Atendimento" },
  { flag: "pode_retomar_atendimento", tipo: "retomar", label: "Retomar Atendimento" },
  // Prescrever não tem flag própria: disponível no mesmo status de "Dar Alta" (Em Atendimento).
  { flag: "pode_dar_alta", tipo: "prescrever", label: "Prescrever" },
  { flag: "pode_solicitar_exames", tipo: "exames", label: "Solicitar Exames" },
  { flag: "pode_dar_alta", tipo: "alta", label: "Dar Alta" },
];

const FLAGS_MEDICAS = ["pode_iniciar_atendimento", "pode_dar_alta", "pode_solicitar_exames", "pode_retomar_atendimento"];

function infoRisco(cor) {
  return cor ? COLORS[cor] : SEM_CLASSIFICACAO;
}

function Vital({ label, valor, unidade }) {
  return (
    <div style={{ background: "oklch(97% 0.006 258)", borderRadius: 12, padding: "10px 12px" }}>
      <div style={{ fontSize: 10.5, color: "oklch(55% 0.015 258)", fontWeight: 700, letterSpacing: "0.03em" }}>
        {label}
        {unidade && <span style={{ fontWeight: 600 }}> · {unidade}</span>}
      </div>
      <div style={{ fontSize: 17, fontWeight: 800, marginTop: 2, fontVariantNumeric: "tabular-nums" }}>{valor ?? "—"}</div>
    </div>
  );
}

function ListaPacientes({ token, showToast, onSelecionarPaciente }) {
  const [pacientes, setPacientes] = useState([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let cancelado = false;
    listarPainel(token)
      .then((dados) => {
        if (!cancelado) setPacientes(dados.filter((p) => FLAGS_MEDICAS.some((f) => p[f])));
      })
      .catch((err) => showToast(err.message || "Erro ao carregar pacientes."))
      .finally(() => {
        if (!cancelado) setCarregando(false);
      });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ fontSize: 14, color: MUTED }}>Selecione um paciente para atender:</div>
      {carregando && <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>}
      {!carregando &&
        pacientes.map((p) => {
          const risco = infoRisco(p.classificacao_risco);
          return (
            <div
              key={p.paciente_id}
              style={{ display: "flex", alignItems: "center", gap: 16, background: "#fff", border: BORDA, borderLeft: `5px solid ${risco.bg}`, borderRadius: 14, padding: "14px 20px" }}
            >
              <div style={{ width: 74, textAlign: "center", padding: "6px 0", borderRadius: 10, background: risco.bg, color: risco.text, fontSize: 11.5, fontWeight: 800, flexShrink: 0 }}>
                {risco.label}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14.5, fontWeight: 700 }}>{p.nome}</div>
                <div style={{ fontSize: 12, color: MUTED }}>{p.status}</div>
              </div>
              <button onClick={() => onSelecionarPaciente(p.paciente_id)} style={{ ...btnPrimario, padding: "9px 16px", fontSize: 13 }}>
                Abrir
              </button>
            </div>
          );
        })}
      {!carregando && pacientes.length === 0 && (
        <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)", fontSize: 14 }}>Nenhum paciente aguardando atendimento médico.</div>
      )}
    </div>
  );
}

function PrescricaoModal({ token, pacienteId, pacienteNome, showToast, onPrescrito, onCancel }) {
  return (
    <div style={{ position: "fixed", inset: 0, background: "oklch(20% 0.02 258 / 0.45)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="prescrever-titulo"
        style={{ background: "#fff", borderRadius: 20, padding: "26px 28px", width: 560, maxWidth: "92vw", maxHeight: "92vh", overflowY: "auto", boxSizing: "border-box", display: "flex", flexDirection: "column", gap: 14 }}
      >
        <div>
          <h2 id="prescrever-titulo" style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>Prescrever</h2>
          <div style={{ fontSize: 12.5, color: MUTED, marginTop: 2 }}>{pacienteNome}</div>
        </div>
        <PrescricaoForm token={token} pacienteId={pacienteId} showToast={showToast} onPrescrito={onPrescrito} />
        <button onClick={onCancel} style={btnSecundario}>
          Cancelar
        </button>
      </div>
    </div>
  );
}

export default function AtendimentoScreen({ token, showToast, pacienteId, onSelecionarPaciente, onVoltar, onAlta }) {
  const [prontuario, setProntuario] = useState(null);
  const [erroCarga, setErroCarga] = useState(null);
  const [modal, setModal] = useState(null);
  // Paciente aberto agora: respostas de um paciente anterior (troca rápida) são descartadas,
  // senão os dados de A poderiam aparecer — e receber ações — na tela de B.
  const pacienteAtual = useRef(pacienteId);
  pacienteAtual.current = pacienteId;

  const recarregar = useCallback(() => {
    const id = pacienteId;
    return consultarProntuario(token, id)
      .then((dados) => {
        if (pacienteAtual.current !== id) return;
        setProntuario(dados);
        setErroCarga(null);
      })
      .catch((err) => {
        if (pacienteAtual.current !== id) return;
        const mensagem = err.message || "Erro ao carregar prontuário.";
        setErroCarga(mensagem);
        showToast(mensagem);
      });
  }, [token, pacienteId, showToast]);

  useEffect(() => {
    if (!pacienteId) return;
    setProntuario(null);
    setErroCarga(null);
    recarregar();
  }, [pacienteId, recarregar]);

  if (!pacienteId) {
    return <ListaPacientes token={token} showToast={showToast} onSelecionarPaciente={onSelecionarPaciente} />;
  }

  if (!prontuario && erroCarga) {
    return (
      <div role="alert" style={{ ...card, display: "flex", flexDirection: "column", gap: 14, alignItems: "flex-start" }}>
        <div style={{ fontSize: 14, fontWeight: 700 }}>Não foi possível carregar o prontuário.</div>
        <div style={{ fontSize: 13, color: MUTED }}>{erroCarga}</div>
        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={recarregar} style={btnPrimario}>
            Tentar novamente
          </button>
          <button onClick={onVoltar} style={btnSecundario}>
            Voltar à lista
          </button>
        </div>
      </div>
    );
  }

  if (!prontuario) {
    return <div style={{ padding: 40, textAlign: "center", color: "oklch(55% 0.015 258)" }}>Carregando...</div>;
  }

  async function onConfirmarAcao(observacoes) {
    const config = ACAO_CONFIG[modal];
    try {
      await config.executar(token, pacienteId, observacoes);
      showToast(config.mensagemSucesso);
      setModal(null);
      if (modal === "alta") {
        onAlta();
        return;
      }
    } catch (err) {
      showToast(err.message || "Erro ao executar ação.");
      setModal(null);
    }
    recarregar();
  }

  const { paciente, sinais_vitais: sv } = prontuario;
  const risco = infoRisco(sv.classificacao_risco);
  const acoes = ACOES.filter((a) => prontuario[a.flag]);
  const idade = calcIdade(paciente.data_nascimento);
  const identificacao = [
    `${idade} ${idade === 1 ? "ano" : "anos"}`,
    SEXO_LABEL[paciente.sexo] || paciente.sexo || "Sexo —",
    `CPF ${formatCPF(paciente.cpf)}`,
    `CNS ${formatCNS(paciente.cns)}`,
    `Tel. ${paciente.telefone || "—"}`,
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <button onClick={onVoltar} style={{ ...btnSecundario, alignSelf: "flex-start", minHeight: 0, padding: "8px 14px", fontSize: 12.5 }}>
        ← Voltar à lista
      </button>

      <section aria-label="Paciente" style={{ ...card, borderLeft: `8px solid ${risco.bg}`, display: "flex", flexDirection: "column", gap: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
          <div style={{ minWidth: 0 }}>
            <h2 style={{ fontSize: 21, fontWeight: 800, margin: 0 }}>{prontuario.paciente_nome}</h2>
            <div style={{ fontSize: 13, color: MUTED, marginTop: 6, display: "flex", flexWrap: "wrap", columnGap: 14, rowGap: 4, fontVariantNumeric: "tabular-nums" }}>
              {identificacao.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <span style={{ padding: "6px 14px", borderRadius: 999, background: risco.bg, color: risco.text, fontSize: 12, fontWeight: 800 }}>{risco.label}</span>
            <span style={{ padding: "6px 14px", borderRadius: 999, background: "oklch(96% 0.008 258)", color: "oklch(40% 0.02 258)", fontSize: 12, fontWeight: 700 }}>
              {prontuario.status}
            </span>
          </div>
        </div>
        {acoes.length > 0 && (
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", paddingTop: 14, borderTop: "1px solid oklch(94% 0.008 258)" }}>
            {acoes.map((a, i) => (
              <button key={a.tipo} onClick={() => setModal(a.tipo)} style={i === 0 ? btnPrimario : btnSecundario}>
                {a.label}
              </button>
            ))}
          </div>
        )}
      </section>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 18, alignItems: "flex-start" }}>
        <section aria-labelledby="triagem-titulo" style={{ ...card, flex: "2 1 420px", minWidth: 0 }}>
          <h3 id="triagem-titulo" style={tituloSecao}>Triagem</h3>
          <div style={{ fontSize: 11, fontWeight: 700, color: "oklch(55% 0.015 258)", textTransform: "uppercase", letterSpacing: "0.03em" }}>Queixa principal</div>
          <div style={{ fontSize: 14.5, marginTop: 4, lineHeight: 1.5 }}>{prontuario.queixa || "—"}</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(84px, 1fr))", gap: 10, marginTop: 18 }}>
            <Vital label="PA" valor={sv.pas != null ? `${sv.pas}/${sv.pad ?? "—"}` : null} unidade="mmHg" />
            <Vital label="FC" valor={sv.fc} unidade="bpm" />
            <Vital label="FR" valor={sv.fr} unidade="irpm" />
            <Vital label="Temp." valor={sv.temp} unidade="°C" />
            <Vital label="SpO2" valor={sv.spo2} unidade="%" />
            <Vital label="Dor" valor={sv.dor} unidade="0–10" />
          </div>
        </section>

        <section aria-labelledby="prescricoes-titulo" style={{ ...card, flex: "1 1 280px", minWidth: 0 }}>
          <h3 id="prescricoes-titulo" style={tituloSecao}>Prescrições</h3>
          {prontuario.prescricoes.map((rx) => (
            <div key={rx.id} style={{ padding: "10px 0", borderTop: "1px solid oklch(94% 0.008 258)" }}>
              <div style={{ fontSize: 13.5, fontWeight: 700 }}>
                {rx.medicamento} — {rx.dosagem}
              </div>
              <div style={{ fontSize: 12, color: MUTED, marginTop: 2 }}>
                {rx.via} · {rx.frequencia || "—"} · {new Date(rx.data).toLocaleString("pt-BR")} · {rx.responsavel_matricula}
              </div>
            </div>
          ))}
          {prontuario.prescricoes.length === 0 && <div style={{ fontSize: 13, color: "oklch(55% 0.015 258)" }}>Nenhuma prescrição registrada.</div>}
        </section>
      </div>

      <section aria-labelledby="evolucao-titulo" style={card}>
        <h3 id="evolucao-titulo" style={tituloSecao}>Evolução</h3>
        <ol style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {prontuario.evolucoes.map((e) => (
            <li key={e.id} style={{ paddingBottom: 18, borderLeft: "2px solid oklch(90% 0.012 258)", marginLeft: 4, paddingLeft: 18, position: "relative" }}>
              <div style={{ position: "absolute", left: -6, top: 2, width: 10, height: 10, borderRadius: "50%", background: ACENTO }} />
              <div style={{ fontSize: 12, color: MUTED }}>
                {new Date(e.data).toLocaleString("pt-BR")} · {e.responsavel_matricula}
              </div>
              <div style={{ fontSize: 11.5, fontWeight: 700, color: "oklch(45% 0.02 258)", marginTop: 2 }}>{e.tipo}</div>
              <div style={{ fontSize: 13, marginTop: 4, lineHeight: 1.5 }}>{e.descricao}</div>
            </li>
          ))}
        </ol>
      </section>

      {modal === "prescrever" && (
        <PrescricaoModal
          token={token}
          pacienteId={pacienteId}
          pacienteNome={prontuario.paciente_nome}
          showToast={showToast}
          onPrescrito={() => {
            setModal(null);
            recarregar();
          }}
          onCancel={() => setModal(null)}
        />
      )}
      {modal && modal !== "prescrever" && (
        <ConfirmModal
          title={ACAO_CONFIG[modal].title}
          description={ACAO_CONFIG[modal].description(prontuario.paciente_nome)}
          confirmLabel={ACAO_CONFIG[modal].confirmLabel}
          showObservacoes={ACAO_CONFIG[modal].showObservacoes}
          onConfirm={onConfirmarAcao}
          onCancel={() => setModal(null)}
        />
      )}
    </div>
  );
}
