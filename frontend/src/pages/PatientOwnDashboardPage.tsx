import { useEffect, useState } from "react";
import { isAxiosError } from "axios";
import { Loader2 } from "lucide-react";
import { getMyDashboard } from "../api/client";
import type { DashboardSchema } from "../types/dashboardSchema";
import PatientPage from "./PatientPage";
import AppHeader from "../components/layout/AppHeader";

export default function PatientOwnDashboardPage() {
  const [schema, setSchema] = useState<DashboardSchema | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMyDashboard()
      .then(setSchema)
      .catch((e: unknown) => {
        const message =
          isAxiosError(e) && typeof e.response?.data?.detail === "string"
            ? e.response.data.detail
            : "Impossible de charger votre tableau de bord.";
        setError(message);
      });
  }, []);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16">
        <AppHeader />
        <p className="text-sm rounded-lg p-3" style={{ background: "var(--clay-soft)", color: "var(--clay)" }}>
          {error}
        </p>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 flex items-center gap-2" style={{ color: "var(--slate)" }}>
        <Loader2 size={16} className="animate-spin" />
        Chargement de votre tableau de bord...
      </div>
    );
  }

  return <PatientPage schema={schema} />;
}
