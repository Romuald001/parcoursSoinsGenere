import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { isAxiosError } from "axios";
import { useMutation } from "@tanstack/react-query";
import { RotateCcw, UserPlus, Loader2 } from "lucide-react";
import type { DashboardSchema } from "../types/dashboardSchema";
import DashboardRenderer from "../components/renderer/DashboardRenderer";
import AppHeader from "../components/layout/AppHeader";
import StepIndicator from "../components/layout/StepIndicator";
import { registerPatientAccount } from "../api/client";

interface Props {
  schema: DashboardSchema;
  patientId?: string | null;
  onRestart?: () => void;
}

function CreatePatientAccountForm({ patientId }: { patientId: string }) {
  const [identifierType, setIdentifierType] = useState<"email" | "phone">("email");
  const [value, setValue] = useState("");
  const [password, setPassword] = useState("");
  const [success, setSuccess] = useState(false);

  const mutation = useMutation({
    mutationFn: () =>
      registerPatientAccount({
        patientId,
        email: identifierType === "email" ? value : undefined,
        phone: identifierType === "phone" ? value : undefined,
        password,
      }),
    onSuccess: () => setSuccess(true),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSuccess(false);
    mutation.mutate();
  }

  return (
    <div
      className="rounded-xl p-5 border mt-8"
      style={{ background: "var(--paper-raised)", borderColor: "var(--border)" }}
    >
      <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--slate)" }}>
        Créer un accès patient
      </p>

      <div className="flex gap-2 mb-3">
        <button
          type="button"
          onClick={() => setIdentifierType("email")}
          className="px-3 py-1.5 rounded-lg text-xs font-medium border"
          style={{
            borderColor: "var(--border)",
            background: identifierType === "email" ? "var(--sage-soft)" : "transparent",
            color: identifierType === "email" ? "var(--sage-deep)" : "var(--slate)",
          }}
        >
          Email
        </button>
        <button
          type="button"
          onClick={() => setIdentifierType("phone")}
          className="px-3 py-1.5 rounded-lg text-xs font-medium border"
          style={{
            borderColor: "var(--border)",
            background: identifierType === "phone" ? "var(--sage-soft)" : "transparent",
            color: identifierType === "phone" ? "var(--sage-deep)" : "var(--slate)",
          }}
        >
          Téléphone
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <input
          type={identifierType === "email" ? "email" : "tel"}
          required
          placeholder={identifierType === "email" ? "Email du patient" : "Numéro de téléphone"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="flex-1 px-3 py-2 rounded-lg border text-sm focus:outline-none"
          style={{ borderColor: "var(--border)", color: "var(--ink)" }}
        />
        <input
          type="password"
          required
          placeholder="Mot de passe temporaire"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="flex-1 px-3 py-2 rounded-lg border text-sm focus:outline-none"
          style={{ borderColor: "var(--border)", color: "var(--ink)" }}
        />
        <button
          type="submit"
          disabled={mutation.isPending}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition hover:brightness-110"
          style={{ background: "var(--sage)" }}
        >
          {mutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <UserPlus size={15} />}
          Créer
        </button>
      </form>

      {success && <p className="text-sm mt-3" style={{ color: "var(--sage)" }}>Accès patient créé avec succès.</p>}
      {mutation.isError && (
        <p className="text-sm mt-3" style={{ color: "var(--clay)" }}>
          {isAxiosError(mutation.error) && typeof mutation.error.response?.data?.detail === "string"
            ? mutation.error.response.data.detail
            : "Impossible de créer cet accès."}
        </p>
      )}
    </div>
  );
}

export default function PatientPage({ schema, patientId, onRestart }: Props) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <div className="max-w-6xl mx-auto px-6 pt-10">
        <AppHeader />
        {onRestart && <StepIndicator current="patient" />}
      </div>
      <DashboardRenderer schema={schema} />
      <div className="max-w-6xl mx-auto px-6 pb-10">
        {onRestart && patientId && <CreatePatientAccountForm patientId={patientId} />}
        {onRestart && (
          <button
            onClick={onRestart}
            className="flex items-center gap-1.5 text-sm font-medium mt-6"
            style={{ color: "var(--slate)" }}
          >
            <RotateCcw size={14} />
            Générer un autre dossier
          </button>
        )}
      </div>
    </motion.div>
  );
}
