import { ACENTO } from "../colors.js";

const NAV_POR_PERFIL = {
  enfermeiro: [
    { key: "painel", label: "Painel" },
    { key: "cadastro", label: "Cadastro de Paciente" },
    { key: "triagem", label: "Triagem" },
    { key: "prontuario", label: "Prontuário" },
  ],
  medico: [
    { key: "painel", label: "Painel" },
    { key: "atendimento", label: "Atendimento" },
    { key: "prontuario", label: "Prontuário" },
    { key: "prescricao", label: "Prescrição" },
  ],
};

const TITULOS = {
  painel: {
    enfermeiro: ["Painel de Atendimento", "Fila geral de pacientes por classificação de risco."],
    medico: ["Painel de Atendimento", "Fila de pacientes triados aguardando atendimento médico."],
  },
  cadastro: { _: ["Cadastro de Paciente", "Registro de novo paciente no sistema."] },
  triagem: { _: ["Triagem", "Classificação de risco pelo Protocolo de Manchester."] },
  atendimento: { _: ["Atendimento", "Início de atendimento médico após triagem."] },
  prontuario: { _: ["Prontuário", "Sinais vitais, evolução e prescrições do paciente."] },
  prescricao: { _: ["Prescrição", "Registro de medicamentos prescritos."] },
};

function navButtonStyle(active) {
  return {
    textAlign: "left",
    border: "none",
    background: active ? "oklch(96% 0.008 258)" : "transparent",
    color: active ? "oklch(24% 0.02 258)" : "oklch(45% 0.018 258)",
    fontWeight: active ? 700 : 600,
    fontSize: 13.5,
    padding: "10px 12px",
    borderRadius: 10,
    cursor: "pointer",
  };
}

const LABEL_PERFIL = { medico: "Médico", enfermeiro: "Enfermeiro" };

export default function Shell({ perfil, matricula, nome, screen, setScreen, onLogout, children }) {
  const navItems = NAV_POR_PERFIL[perfil];
  const [title, subtitle] = TITULOS[screen]?.[perfil] || TITULOS[screen]?._ || ["", ""];
  const identificacao = nome ? `${nome} (${LABEL_PERFIL[perfil]})` : LABEL_PERFIL[perfil];

  return (
    <div style={{ display: "flex", width: "100%", height: "100%" }}>
      <div
        style={{
          width: 236,
          flexShrink: 0,
          background: "#ffffff",
          borderRight: "1px solid oklch(90% 0.012 258)",
          display: "flex",
          flexDirection: "column",
          padding: "24px 16px",
          gap: 4,
          boxSizing: "border-box",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 8px 24px 8px" }}>
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 12,
              background: ACENTO,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 800,
              fontSize: 15,
              flexShrink: 0,
            }}
          >
            UN
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontWeight: 800, fontSize: 14, lineHeight: 1.2 }}>UPA Nordeste</div>
            <div style={{ fontSize: 11, color: "oklch(50% 0.018 258)" }}>Sistema Hospitalar</div>
          </div>
        </div>
        {navItems.map((item) => (
          <button key={item.key} onClick={() => setScreen(item.key)} style={navButtonStyle(screen === item.key)}>
            {item.label}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "18px 32px",
            borderBottom: "1px solid oklch(90% 0.012 258)",
            background: "#ffffff",
            flexShrink: 0,
          }}
        >
          <div>
            <div style={{ fontSize: 20, fontWeight: 800 }}>{title}</div>
            <div style={{ fontSize: 13, color: "oklch(50% 0.018 258)", marginTop: 2 }}>{subtitle}</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{identificacao}</div>
              <div style={{ fontSize: 11, color: "oklch(50% 0.018 258)" }}>Matrícula {matricula}</div>
            </div>
            <button
              onClick={onLogout}
              style={{
                border: "1px solid oklch(88% 0.012 258)",
                background: "#fff",
                padding: "8px 14px",
                borderRadius: 10,
                fontSize: 13,
                fontWeight: 600,
                color: "oklch(40% 0.02 258)",
                cursor: "pointer",
              }}
            >
              Sair
            </button>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "28px 32px", boxSizing: "border-box" }}>{children}</div>
      </div>
    </div>
  );
}
