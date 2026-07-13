# Interfaces e Integrações

## 1. Protótipos
* Protótipo interativo: `docs/prototipo/projeto/Prototipo Hospitalar.dc.html` (telas: Login, Painel, Cadastro, Triagem, Prontuário, Prescrição).
* Screenshots de referência: `docs/prototipo/projeto/screenshots/`.

## 2. Hardware
* Leitor de código de barras: leitura do cartão CNS / pulseira de identificação do paciente no cadastro e na triagem.
* Impressora térmica: emissão de pulseira/etiqueta de identificação do paciente após o cadastro.

## 3. Software
* Integração com AGHU (Aplicação de Gestão para Hospitais Universitários) para sincronização futura de prontuário — fora de escopo desta fase (ver `01-visao.md`); interface abaixo definida para viabilizar a integração posteriormente.

### [SCHEMA] Interface de Integração (TypeScript)
```typescript
interface PatientRecord {
  id: string;
  nome: string;
  cpf: string;
  cns: string;
}

interface ProntuarioUpdate {
  pacienteId: string;
  evolucao: string;
}

interface AuthStatus {
  autenticado: boolean;
  token?: string;
}

interface SyncResponse {
  sucesso: boolean;
  mensagem?: string;
}

interface IHospitalApi {
  getPatientData(id: string): Promise<PatientRecord>;
  syncProntuario(data: ProntuarioUpdate): Promise<SyncResponse>;
  checkCredentials(matricula: string, pin: string): Promise<AuthStatus>;
}
```
