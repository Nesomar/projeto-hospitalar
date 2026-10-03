import { useState } from "react";
import { prescrever } from "../api.js";

function defaultForm() {
  return { medicamento: "", dosagem: "", via: "Oral", frequencia: "", observacoes: "" };
}

const inputStyle = { width: "100%", border: "1px solid oklch(88% 0.012 258)", borderRadius: 12, padding: "11px 14px", fontSize: 14, boxSizing: "border-box" };

export default function PrescricaoForm({ token, pacienteId, showToast, onPrescrito }) {
  const [form, setForm] = useState(defaultForm());
  const [enviando, setEnviando] = useState(false);

  function update(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function onSubmit() {
    if (!form.medicamento || !form.dosagem) {
      showToast("Informe medicamento e dosagem.");
      return;
    }
    setEnviando(true);
    try {
      await prescrever(token, pacienteId, {
        medicamento: form.medicamento,
        dosagem: form.dosagem,
        via: form.via,
        frequencia: form.frequencia || undefined,
        observacoes: form.observacoes || undefined,
      });
      showToast("Prescrição registrada.");
      setForm(defaultForm());
      onPrescrito(pacienteId);
    } catch (err) {
      showToast(err.message || "Erro ao registrar prescrição.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <label htmlFor="rx-medicamento" style={{ fontSize: 12, fontWeight: 700 }}>Medicamento</label>
        <input
          id="rx-medicamento"
          type="text"
          value={form.medicamento}
          onChange={(e) => update("medicamento", e.target.value)}
          placeholder="ex: Dipirona"
          style={inputStyle}
        />
      </div>
      <div style={{ display: "flex", gap: 14 }}>
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 6 }}>
          <label htmlFor="rx-dosagem" style={{ fontSize: 12, fontWeight: 700 }}>Dosagem</label>
          <input id="rx-dosagem" type="text" value={form.dosagem} onChange={(e) => update("dosagem", e.target.value)} placeholder="500mg" style={inputStyle} />
        </div>
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 6 }}>
          <label htmlFor="rx-via" style={{ fontSize: 12, fontWeight: 700 }}>Via</label>
          <select id="rx-via" value={form.via} onChange={(e) => update("via", e.target.value)} style={{ ...inputStyle, background: "#fff" }}>
            <option value="Oral">Oral</option>
            <option value="IV">Endovenosa</option>
            <option value="IM">Intramuscular</option>
            <option value="SC">Subcutânea</option>
            <option value="Tópica">Tópica</option>
          </select>
        </div>
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 6 }}>
          <label htmlFor="rx-frequencia" style={{ fontSize: 12, fontWeight: 700 }}>Frequência</label>
          <input id="rx-frequencia" type="text" value={form.frequencia} onChange={(e) => update("frequencia", e.target.value)} placeholder="8/8h" style={inputStyle} />
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <label htmlFor="rx-observacoes" style={{ fontSize: 12, fontWeight: 700 }}>Observações</label>
        <textarea
          id="rx-observacoes"
          value={form.observacoes}
          onChange={(e) => update("observacoes", e.target.value)}
          placeholder="Observações adicionais..."
          style={{ ...inputStyle, fontSize: 13, minHeight: 70, resize: "vertical" }}
        />
      </div>
      <button
        onClick={onSubmit}
        disabled={enviando}
        style={{ border: "none", background: "#2F6FED", color: "#fff", padding: 13, borderRadius: 12, fontSize: 14, fontWeight: 700, cursor: "pointer" }}
      >
        {enviando ? "Salvando..." : "Salvar Prescrição"}
      </button>
    </>
  );
}
