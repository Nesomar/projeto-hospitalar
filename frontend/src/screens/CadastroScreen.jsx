import { useState } from "react";
import { s } from "../styles.js";
import { cadastrarPaciente } from "../api.js";

function defaultForm() {
  return { nome: "", cpf: "", cns: "", data_nascimento: "", sexo: "F", telefone: "" };
}

export default function CadastroScreen({ token, showToast, onCadastrado }) {
  const [form, setForm] = useState(defaultForm());
  const [erroCpf, setErroCpf] = useState(false);
  const [erroCns, setErroCns] = useState(false);
  const [enviando, setEnviando] = useState(false);

  function update(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function onSubmit() {
    const cpfDigits = form.cpf.replace(/\D/g, "");
    const cnsDigits = form.cns.replace(/\D/g, "");
    const invalidoCpf = cpfDigits.length !== 11;
    const invalidoCns = cnsDigits.length !== 15;
    setErroCpf(invalidoCpf);
    setErroCns(invalidoCns);
    if (!form.nome || form.nome.trim().length < 3 || invalidoCpf || invalidoCns || !form.data_nascimento) {
      showToast("Verifique os campos obrigatórios do cadastro.");
      return;
    }
    setEnviando(true);
    try {
      await cadastrarPaciente(token, {
        nome: form.nome.trim(),
        cpf: cpfDigits,
        cns: cnsDigits,
        data_nascimento: form.data_nascimento,
        sexo: form.sexo,
        telefone: form.telefone || null,
      });
      showToast("Paciente cadastrado com sucesso.");
      setForm(defaultForm());
      onCadastrado();
    } catch (err) {
      showToast(err.message || "Erro ao cadastrar paciente.");
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
      <div style={{ fontSize: 15, fontWeight: 700 }}>Dados do Paciente</div>
      <div style={s.field}>
        <label style={s.label}>Nome completo</label>
        <input
          type="text"
          value={form.nome}
          onChange={(e) => update("nome", e.target.value)}
          placeholder="Nome completo do paciente"
          style={s.input}
        />
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>CPF (11 dígitos)</label>
          <input
            type="text"
            value={form.cpf}
            onChange={(e) => update("cpf", e.target.value)}
            placeholder="00000000000"
            style={{ ...s.input, fontFamily: "ui-monospace, monospace" }}
          />
          {erroCpf && <div style={s.errorText}>CPF deve ter 11 dígitos numéricos.</div>}
        </div>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>CNS (15 dígitos)</label>
          <input
            type="text"
            value={form.cns}
            onChange={(e) => update("cns", e.target.value)}
            placeholder="000000000000000"
            style={{ ...s.input, fontFamily: "ui-monospace, monospace" }}
          />
          {erroCns && <div style={s.errorText}>CNS deve ter 15 dígitos numéricos.</div>}
        </div>
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>Data de nascimento</label>
          <input
            type="date"
            value={form.data_nascimento}
            onChange={(e) => update("data_nascimento", e.target.value)}
            style={s.input}
          />
        </div>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>Sexo</label>
          <select value={form.sexo} onChange={(e) => update("sexo", e.target.value)} style={{ ...s.input, background: "#fff" }}>
            <option value="F">Feminino</option>
            <option value="M">Masculino</option>
            <option value="O">Outro</option>
          </select>
        </div>
        <div style={{ flex: 1, minWidth: 0, ...s.field }}>
          <label style={s.label}>Telefone</label>
          <input
            type="text"
            value={form.telefone}
            onChange={(e) => update("telefone", e.target.value)}
            placeholder="(00) 00000-0000"
            style={s.input}
          />
        </div>
      </div>
      <button
        onClick={onSubmit}
        disabled={enviando}
        style={{ ...s.btnPrimary, marginTop: 6, alignSelf: "flex-start", padding: "12px 22px" }}
      >
        {enviando ? "Cadastrando..." : "Cadastrar Paciente"}
      </button>
    </div>
  );
}
