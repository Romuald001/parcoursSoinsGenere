import { useState } from "react";
import { FilePlus, Users } from "lucide-react";
import AppHeader from "../components/layout/AppHeader";
import DoctorFlow from "./DoctorFlow";
import PatientListPage from "./PatientListPage";
import PatientDetailPage from "./PatientDetailPage";

type Tab = "new" | "patients";

export default function DoctorHome() {
  const [tab, setTab] = useState<Tab>("new");
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);

  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 pt-10">
        <AppHeader />
        <div className="flex gap-2 mb-2 print:hidden">
          <button
            onClick={() => { setTab("new"); setSelectedPatientId(null); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border"
            style={{
              borderColor: "var(--border)",
              background: tab === "new" ? "var(--sage-soft)" : "transparent",
              color: tab === "new" ? "var(--sage-deep)" : "var(--slate)",
            }}
          >
            <FilePlus size={13} /> Nouvelle consultation
          </button>
          <button
            onClick={() => setTab("patients")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border"
            style={{
              borderColor: "var(--border)",
              background: tab === "patients" ? "var(--sage-soft)" : "transparent",
              color: tab === "patients" ? "var(--sage-deep)" : "var(--slate)",
            }}
          >
            <Users size={13} /> Mes patients
          </button>
        </div>
      </div>

      {tab === "new" && <DoctorFlow />}
      {tab === "patients" && !selectedPatientId && (
        <PatientListPage onSelectPatient={setSelectedPatientId} />
      )}
      {tab === "patients" && selectedPatientId && (
        <PatientDetailPage patientId={selectedPatientId} onBack={() => setSelectedPatientId(null)} />
      )}
    </div>
  );
}
