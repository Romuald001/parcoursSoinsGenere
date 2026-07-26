import { useState } from "react";
import { isAxiosError } from "axios";
import { useAuth } from "./context/useAuth";
import LoginPage from "./pages/LoginPage";
import DoctorPage from "./pages/DoctorPage";
import ModelPage from "./pages/ModelPage";
import PatientPage from "./pages/PatientPage";
import PatientOwnDashboardPage from "./pages/PatientOwnDashboardPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import {
  extractPatientRecord,
  validatePatientRecord,
  personalizeSummary,
  generateUI,
  type PatientRecord,
} from "./api/client";
import type { DashboardSchema } from "./types/dashboardSchema";

type Step = "doctor" | "model" | "patient";

function extractErrorMessage(e: unknown, fallback: string): string {
  if (isAxiosError(e) && typeof e.response?.data?.detail === "string") {
    return e.response.data.detail;
  }
  return fallback;
}

function DoctorFlow() {
  const [step, setStep] = useState<Step>("doctor");
  const [record, setRecord] = useState<PatientRecord | null>(null);
  const [schema, setSchema] = useState<DashboardSchema | null>(null);
  const [patientId, setPatientId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleExtract(rawNote: string) {
    setLoading(true);
    setError(null);
    try {
      const extracted = await extractPatientRecord(rawNote);
      const validated = await validatePatientRecord(extracted);
      setRecord(validated);
      setStep("model");
    } catch (e: unknown) {
      setError(extractErrorMessage(e, "Impossible d'analyser cette note. Vérifiez le format ou réessayez."));
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateDashboard() {
    if (!record) return;
    setLoading(true);
    setError(null);
    try {
      const summary = await personalizeSummary(record);
      const { schema: dashboard, patientId: id } = await generateUI(record, summary);
      setSchema(dashboard);
      setPatientId(id);
      setStep("patient");
    } catch (e: unknown) {
      setError(extractErrorMessage(e, "Impossible de générer le tableau de bord. Réessayez."));
    } finally {
      setLoading(false);
    }
  }

  function handleRestart() {
    setRecord(null);
    setSchema(null);
    setPatientId(null);
    setError(null);
    setStep("doctor");
  }

  if (step === "doctor") {
    return <DoctorPage onSubmit={handleExtract} loading={loading} error={error} />;
  }
  if (step === "model" && record) {
    return (
      <ModelPage
        record={record}
        onConfirm={handleGenerateDashboard}
        onBack={() => setStep("doctor")}
        loading={loading}
        error={error}
      />
    );
  }
  if (step === "patient" && schema) {
    return <PatientPage schema={schema} patientId={patientId} onRestart={handleRestart} />;
  }
  return null;
}

function App() {
  const { token, role } = useAuth();

  if (!token) return <LoginPage />;
  if (role === "admin") return <AdminDashboardPage />;
  if (role === "patient") return <PatientOwnDashboardPage />;
  return <DoctorFlow />;
}

export default App;
