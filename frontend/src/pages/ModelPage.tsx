import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, ArrowLeft, ChevronDown, Pill, Stethoscope, Target, Calendar, type LucideIcon } from "lucide-react";
import StepIndicator from "../components/layout/StepIndicator";
import type { PatientRecord } from "../api/client";
import PageShell from "../components/layout/PageShell";

interface Props {
  record: PatientRecord;
  onConfirm: () => void;
  onBack: () => void;
  loading: boolean;
  error: string | null;
}

interface DiagnosticItem {
  label: string;
  icd10_code?: string | null;
}

interface MedicationItem {
  name: string;
  dosage: string;
  frequency: string;
}

interface GoalItem {
  label: string;
  unit?: string | null;
  current_value?: number;
  target_value?: number;
}

interface AppointmentItem {
  label: string;
  location?: string | null;
}

interface AlertItem {
  severity: "info" | "warning" | "critical";
  message: string;
}

const SEVERITY_STYLE: Record<string, { bg: string; fg: string; label: string }> = {
  info: { bg: "var(--info-soft)", fg: "var(--info)", label: "Information" },
  warning: { bg: "var(--amber-soft)", fg: "var(--amber)", label: "À vérifier" },
  critical: { bg: "var(--clay-soft)", fg: "var(--clay)", label: "Important" },
};

function SummaryRow({ icon: Icon, title, subtitle }: { icon: LucideIcon; title: string; subtitle?: string }) {
  return (
    <div className="flex items-start gap-3 py-2.5">
      <Icon size={16} style={{ color: "var(--sage)" }} className="mt-0.5 shrink-0" />
      <div>
        <p className="text-sm font-medium" style={{ color: "var(--ink)" }}>{title}</p>
        {subtitle && <p className="text-xs font-mono mt-0.5" style={{ color: "var(--slate)" }}>{subtitle}</p>}
      </div>
    </div>
  );
}

export default function ModelPage({ record, onConfirm, onBack, loading, error }: Props) {
  const [showRawJson, setShowRawJson] = useState(false);

  const diagnostics = (record.diagnostics as DiagnosticItem[] | undefined) ?? [];
  const medications = (record.medications as MedicationItem[] | undefined) ?? [];
  const goals = (record.clinical_goals as GoalItem[] | undefined) ?? [];
  const appointments = (record.appointments as AppointmentItem[] | undefined) ?? [];
  const alerts = (record.alerts as AlertItem[] | undefined) ?? [];

  return (
    <PageShell>
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-2xl mx-auto px-4 py-10"
    >
      <StepIndicator current="model" />

      <h1 className="text-3xl mb-2" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Dossier extrait
      </h1>
      <p className="text-sm mb-6" style={{ color: "var(--slate)" }}>
        Voici ce que le système a compris de la note. Vérifiez les alertes
        avant de générer le tableau de bord du patient.
      </p>

      {alerts.length > 0 && (
        <div className="flex flex-col gap-2 mb-6">
          {alerts.map((alert, i) => {
            const style = SEVERITY_STYLE[alert.severity] ?? SEVERITY_STYLE.info;
            return (
              <div
                key={i}
                className="rounded-lg p-3 text-sm border-l-4"
                style={{ background: style.bg, borderLeftColor: style.fg, color: "var(--ink)" }}
              >
                <span className="text-xs font-semibold uppercase mr-2" style={{ color: style.fg }}>
                  {style.label}
                </span>
                {alert.message}
              </div>
            );
          })}
        </div>
      )}

      <div
        className="rounded-xl border divide-y mb-4"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        <div className="px-4">
          {diagnostics.map((d, i) => (
            <SummaryRow key={`d-${i}`} icon={Stethoscope} title={d.label} subtitle={d.icd10_code ?? undefined} />
          ))}
          {medications.map((m, i) => (
            <SummaryRow key={`m-${i}`} icon={Pill} title={m.name} subtitle={`${m.dosage} — ${m.frequency}`} />
          ))}
          {goals.map((g, i) => (
            <SummaryRow
              key={`g-${i}`}
              icon={Target}
              title={g.label}
              subtitle={g.unit ? `${g.current_value}${g.unit} → ${g.target_value}${g.unit}` : undefined}
            />
          ))}
          {appointments.map((a, i) => (
            <SummaryRow key={`a-${i}`} icon={Calendar} title={a.label} subtitle={a.location ?? undefined} />
          ))}
        </div>
      </div>

      <button
        onClick={() => setShowRawJson(!showRawJson)}
        className="flex items-center gap-1.5 text-xs font-medium mb-6"
        style={{ color: "var(--slate)" }}
      >
        <ChevronDown size={14} style={{ transform: showRawJson ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
        {showRawJson ? "Masquer" : "Afficher"} le JSON technique
      </button>

      <AnimatePresence>
        {showRawJson && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden mb-6"
          >
            <div
              className="rounded-xl p-4 border overflow-auto"
              style={{ background: "var(--paper-raised)", borderColor: "var(--border)", maxHeight: 300 }}
            >
              <pre className="text-xs font-mono" style={{ color: "var(--ink)" }}>
                {JSON.stringify(record, null, 2)}
              </pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-3">
        <button
          onClick={onConfirm}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition hover:brightness-110"
          style={{ background: "var(--sage)" }}
        >
          {loading && <Loader2 size={15} className="animate-spin" />}
          {loading ? "Génération en cours..." : "Valider et générer le tableau de bord"}
        </button>
        <button
          onClick={onBack}
          disabled={loading}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium border disabled:opacity-40 transition hover:bg-black/[0.02]"
          style={{ borderColor: "var(--border)", color: "var(--slate)" }}
        >
          <ArrowLeft size={14} />
          Revenir à la note
        </button>
      </div>

      {error && (
        <p className="mt-4 text-sm rounded-lg p-3" style={{ background: "var(--clay-soft)", color: "var(--clay)" }}>
          {error}
        </p>
      )}
    </motion.div>
    </PageShell>
  );
}
