import { useState } from "react";
import { s } from "../styles.js";
import { abrirNovoAtendimento, ApiError, buscarPacientePorCpf, cadastrarPaciente } from "../api.js";

function defaultForm() {
  return { nome: "", cpf: "", cns: "", data_nascimento: "", sexo: "F", telefone: "" };
}

// input type="date" sempre entrega yyyy-mm-dd, mas tolera-se tambem dd/mm/yyyy
// (autofill, colar texto, navegador sem suporte nativo ao widget de data).
function normalizarDataISO(valor) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) return valor;
  const match = valor.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (match) return `${match[3]}-${match[2]}-${match[1]}`;
  return null;
}

export default function CadastroScreen({ token, showToast, onCadastrado }) {
  const [form, setForm] = useState(defaultForm());
  const [erroCpf, setErroCpf] = useState(false);
  const [erroCns, setErroCns] = useState(false);
  const [enviando, setEnviando] = useState(false);
  // Paciente já cadastrado (CPF repetido): oferece abrir novo atendimento em vez de só mostrar o erro.
  const [retorno, setRetorno] = useState(null);

  function update(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function onSubmit() {
    const cpfDigits = form.cpf.replace(/\D/g, "");
    const cnsDigits = form.cns.replace(/\D/g, "");
    const invalidoCpf = cpfDigits.length !== 11;
    const invalidoCns = cnsDigits.length !== 15;
    const dataNascimentoISO = normalizarDataISO(form.data_nascimento);
    setErroCpf(invalidoCpf);
    setErroCns(invalidoCns);
    if (!form.nome || form.nome.trim().length < 3 || invalidoCpf || invalidoCns || !dataNascimentoISO) {
      showToast("Verifique os campos obrigatórios do cadastro.");
      return;
    }
    setEnviando(true);
    try {
      await cadastrarPaciente(token, {
        nome: form.nome.trim(),
        cpf: cpfDigits,
        cns: cnsDigits,
        data_nascimento: dataNascimentoISO,
        sexo: form.sexo,
        telefone: form.telefone || null,
      });
      showToast("Paciente cadastrado com sucesso.");
      setForm(defaultForm());
      onCadastrado();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        await tratarCpfJaCadastrado(cpfDigits, err.message);
      } else {
        showToast(err.message || "Erro ao cadastrar paciente.");
      }
    } finally {
      setEnviando(false);
    }
  }

  async function tratarCpfJaCadastrado(cpfDigits, mensagem) {
    try {
      const [paciente] = await buscarPacientePorCpf(token, cpfDigits);
      if (paciente) setRetorno(paciente);
      else showToast(mensagem); // conflito só de CNS: não há paciente por CPF
    } catch (e) {
      showToast(e.message || mensagem);
    }
  }

  async function onAbrirAtendimento() {
    setEnviando(true);
    try {
      await abrirNovoAtendimento(token, retorno.id);
      showToast("Novo atendimento aberto.");
      setRetorno(null);
      setForm(defaultForm());
      onCadastrado();
    } catch (err) {
      showToast(err.message || "Erro ao abrir novo atendimento.");
    } finally {
      setEnviando(false);
    }
  }

  if (retorno) {
    return (
      <div style={{ ...s.card, maxWidth: 640, display: "flex", flexDirection: "column", gap: 16 }}>
        <div style={{ fontSize: 15, fontWeight: 700 }}>Paciente já cadastrado</div>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700 }}>{retorno.nome}</div>
          <div style={{ fontSize: 13, color: "oklch(45% 0.02 258)", marginTop: 4 }}>
            Nascimento: {retorno.data_nascimento.split("-").reverse().join("/")}
          </div>
        </div>
        {retorno.atendimento_ativo ? (
          <div role="status" style={{ fontSize: 14, fontWeight: 600, color: "#B45309" }}>
            Paciente já está em atendimento.
          </div>
        ) : (
          <div style={{ fontSize: 13.5, color: "oklch(40% 0.02 258)" }}>
            O paciente retorna à unidade. Abra um novo atendimento para ele aguardar a triagem.
          </div>
        )}
        <div style={{ display: "flex", gap: 12 }}>
          {!retorno.atendimento_ativo && (
            <button onClick={onAbrirAtendimento} disabled={enviando} style={{ ...s.btnPrimary, padding: "12px 22px" }}>
              {enviando ? "Abrindo..." : "Abrir novo atendimento"}
            </button>
          )}
          <button onClick={() => setRetorno(null)} disabled={enviando} style={s.btnSecondary}>
            Voltar ao cadastro
          </button>
        </div>
      </div>
    );
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
