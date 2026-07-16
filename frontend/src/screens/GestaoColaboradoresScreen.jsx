import { useState } from "react";
import { s } from "../styles.js";
import { cadastrarColaborador } from "../api.js";

const MATRICULA_PATTERN = /^[0-9]{6}$/;
const PIN_PATTERN = /^[0-9]{4}$/;

function defaultForm() {
  return { matricula: "", pin: "", nome: "", perfil: "enfermeiro" };
}

export default function GestaoColaboradoresScreen({ token, showToast }) {
  const [form, setForm] = useState(defaultForm());
  const [erroMatricula, setErroMatricula] = useState(false);
  const [erroPin, setErroPin] = useState(false);
  const [erroNome, setErroNome] = useState(false);
  const [enviando, setEnviando] = useState(false);

  function update(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function onSubmit() {
    const nomeValido = form.nome.trim().length > 0;
    const invalidoMatricula = !MATRICULA_PATTERN.test(form.matricula);
    const invalidoPin = !PIN_PATTERN.test(form.pin);
    setErroMatricula(invalidoMatricula);
    setErroPin(invalidoPin);
    setErroNome(!nomeValido);
    if (invalidoMatricula || invalidoPin || !nomeValido) {
      showToast("Verifique os campos obrigatórios do cadastro.");
      return;
    }
    setEnviando(true);
    try {
      await cadastrarColaborador(token, {
        matricula: form.matricula,
        pin: form.pin,
        nome: form.nome.trim(),
        perfil: form.perfil,
      });
      showToast("Colaborador cadastrado com sucesso.");
      setForm(defaultForm());
    } catch (err) {
      showToast(err.message || "Erro ao cadastrar colaborador.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: 640,
        background: "#fff",
        borderRadius: 20,
        border: "1px solid oklch(90% 0.012 258)",
        padding: "28px 32px",
        display: "flex",
        flexDirection: "column",
        gap: 16,
        boxSizing: "border-box",
      }}
    >
      <div style={{ fontSize: 15, fontWeight: 700 }}>Dados do Colaborador</div>
      <div style={s.field}>
        <label style={s.label}>Nome completo</label>
        <input
          type="text"
          value={form.nome}
          onChange={(e) => update("nome", e.target.value)}
          placeholder="Nome completo do colaborador"
          style={s.input}
        />
        {erroNome && <div style={s.errorText}>Nome é obrigatório.</div>}
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>Matrícula (6 dígitos)</label>
          <input
            type="text"
            value={form.matricula}
            onChange={(e) => update("matricula", e.target.value.replace(/\D/g, "").slice(0, 6))}
            placeholder="000123"
            inputMode="numeric"
            style={{ ...s.input, fontFamily: "ui-monospace, monospace" }}
          />
          {erroMatricula && <div style={s.errorText}>Matrícula deve ter 6 dígitos numéricos.</div>}
        </div>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>PIN inicial (4 dígitos)</label>
          <input
            type="password"
            value={form.pin}
            onChange={(e) => update("pin", e.target.value.replace(/\D/g, "").slice(0, 4))}
            placeholder="••••"
            inputMode="numeric"
            style={{ ...s.input, fontFamily: "ui-monospace, monospace" }}
          />
          {erroPin && <div style={s.errorText}>PIN deve ter 4 dígitos numéricos.</div>}
        </div>
      </div>
      <div style={s.field}>
        <label style={s.label}>Perfil</label>
        <select value={form.perfil} onChange={(e) => update("perfil", e.target.value)} style={{ ...s.input, background: "#fff" }}>
          <option value="enfermeiro">Enfermeiro</option>
          <option value="medico">Médico</option>
        </select>
      </div>
      <button
        onClick={onSubmit}
        disabled={enviando}
        style={{ ...s.btnPrimary, marginTop: 6, alignSelf: "flex-start", padding: "12px 22px" }}
      >
        {enviando ? "Cadastrando..." : "Cadastrar Colaborador"}
      </button>
    </div>
  );
}
