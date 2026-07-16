import { useCallback, useEffect, useRef, useState } from "react";
import Shell from "./components/Shell.jsx";
import Toast from "./components/Toast.jsx";
import LoginScreen from "./screens/LoginScreen.jsx";
import PainelScreen from "./screens/PainelScreen.jsx";
import CadastroScreen from "./screens/CadastroScreen.jsx";
import TriagemScreen from "./screens/TriagemScreen.jsx";
import ProntuarioScreen from "./screens/ProntuarioScreen.jsx";
import PrescricaoScreen from "./screens/PrescricaoScreen.jsx";
import IniciarAtendimentoScreen from "./screens/IniciarAtendimentoScreen.jsx";
import GestaoColaboradoresScreen from "./screens/GestaoColaboradoresScreen.jsx";
import { decodeToken, carregarSessao, salvarToken, removerToken } from "./auth.js";
import { setUnauthorizedHandler } from "./api.js";

export default function App() {
  const [sessao, setSessao] = useState(() => carregarSessao());
  const [screen, setScreenState] = useState(() => (carregarSessao()?.perfil === "administrador" ? "gestao" : "painel"));
  const [pacienteId, setPacienteId] = useState(null);
  const [painelKey, setPainelKey] = useState(0);
  const [toastMsg, setToastMsg] = useState(null);
  const toastTimer = useRef(null);

  const showToast = useCallback((msg) => {
    setToastMsg(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToastMsg(null), 2600);
  }, []);

  function irPara(novaTela, novoPacienteId = null) {
    setScreenState(novaTela);
    setPacienteId(novoPacienteId);
  }

  function voltarAoPainel() {
    irPara("painel");
    setPainelKey((k) => k + 1);
  }

  function onLoginSuccess(token) {
    salvarToken(token);
    const { matricula, perfil, nome } = decodeToken(token);
    setSessao({ token, matricula, perfil, nome });
    irPara(perfil === "administrador" ? "gestao" : "painel");
  }

  function onLogout() {
    removerToken();
    setSessao(null);
  }

  function onSetScreen(novaTela) {
    irPara(novaTela);
  }

  useEffect(() => {
    setUnauthorizedHandler(() => {
      onLogout();
      showToast("Sessão expirada. Faça login novamente.");
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showToast]);

  if (!sessao) {
    return (
      <>
        <LoginScreen onLoginSuccess={onLoginSuccess} showToast={showToast} />
        <Toast message={toastMsg} />
      </>
    );
  }

  return (
    <div style={{ width: "100vw", height: "100vh", background: "oklch(97% 0.006 258)", display: "flex", overflow: "hidden", boxSizing: "border-box" }}>
      <Shell perfil={sessao.perfil} matricula={sessao.matricula} nome={sessao.nome} screen={screen} setScreen={onSetScreen} onLogout={onLogout}>
        {screen === "painel" && (
          <PainelScreen
            key={painelKey}
            token={sessao.token}
            showToast={showToast}
            onAbrirTriagem={(id) => irPara("triagem", id)}
            onAbrirProntuario={(id) => irPara("prontuario", id)}
            onAbrirIniciarAtendimento={(id) => irPara("atendimento", id)}
          />
        )}
        {screen === "cadastro" && <CadastroScreen token={sessao.token} showToast={showToast} onCadastrado={voltarAoPainel} />}
        {screen === "gestao" && <GestaoColaboradoresScreen token={sessao.token} showToast={showToast} />}
        {screen === "triagem" && (
          <TriagemScreen
            token={sessao.token}
            showToast={showToast}
            pacienteId={pacienteId}
            onSelecionarPaciente={(id) => setPacienteId(id)}
            onCancelar={() => setPacienteId(null)}
            onConfirmado={voltarAoPainel}
          />
        )}
        {screen === "atendimento" && (
          <IniciarAtendimentoScreen
            token={sessao.token}
            showToast={showToast}
            pacienteId={pacienteId}
            onSelecionarPaciente={(id) => setPacienteId(id)}
            onCancelar={() => setPacienteId(null)}
            onConfirmado={voltarAoPainel}
          />
        )}
        {screen === "prontuario" && (
          <ProntuarioScreen
            token={sessao.token}
            showToast={showToast}
            pacienteId={pacienteId}
            onSelecionarPaciente={(id) => setPacienteId(id)}
            onNovaPrescricao={(id) => irPara("prescricao", id)}
            onVoltarPainel={voltarAoPainel}
          />
        )}
        {screen === "prescricao" && (
          <PrescricaoScreen
            token={sessao.token}
            matricula={sessao.matricula}
            showToast={showToast}
            pacienteId={pacienteId}
            onSelecionarPaciente={(id) => setPacienteId(id)}
            onPrescrito={(id) => irPara("prontuario", id)}
          />
        )}
      </Shell>
      <Toast message={toastMsg} />
    </div>
  );
}
