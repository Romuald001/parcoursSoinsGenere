import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";
import { ArrowLeft, Loader2, Calendar, Stethoscope, Sparkles } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import {
  getPatientConsultations,
  getGoalTrend,
  getConsultationDashboard,
  continueConsultation,
} from "../api/client";
import type { DashboardSchema } from "../types/dashboardSchema";
import PatientPage from "./PatientPage";

interface Props {
  patientId: string;
  onBack: () => void;
}

export default function PatientDetailPage({ patientId, onBack }: Props) {
  const queryClient = useQueryClient();
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [viewedDashboard, setViewedDashboard] = useState<{ schema: DashboardSchema; doctorName: string | null } | null>(null);
  const [followUpNote, setFollowUpNote] = useState("");

  const { data: consultations, isLoading } = useQuery({
    queryKey: ["consultations", patientId],
    queryFn: () => getPatientConsultations(patientId),
  });

  const goalLabels = Array.from(
    new Set(consultations?.flatMap((c) => c.clinical_goals.map((g) => g.label)) ?? [])
  );

  const { data: trend } = useQuery({
    queryKey: ["goal-trend", patientId, selectedGoal],
    queryFn: () => getGoalTrend(patientId, selectedGoal as string),
    enabled: !!selectedGoal,
  });

  const viewMutation = useMutation({
    mutationFn: (consultationId: string) => getConsultationDashboard(patientId, consultationId),
    onSuccess: setViewedDashboard,
  });

  const continueMutation = useMutation({
    mutationFn: (note: string) => continueConsultation(patientId, note),
    onSuccess: (result) => {
      setViewedDashboard(result);
      setFollowUpNote("");
      queryClient.invalidateQueries({ queryKey: ["consultations", patientId] });
    },
  });

  function handleFollowUpSubmit(e: FormEvent) {
    e.preventDefault();
    continueMutation.mutate(followUpNote);
  }

  // Vue dashboard (consultation passée revue, ou nouvelle mise à jour générée)
  if (viewedDashboard) {
    return (
      <div>
        <div className="max-w-6xl mx-auto px-6 pt-4">
          <button
            onClick={() => setViewedDashboard(null)}
            className="flex items-center gap-1.5 text-sm font-medium print:hidden"
            style={{ color: "var(--slate)" }}
          >
            <ArrowLeft size={14} /> Retour à l'historique
          </button>
        </div>
        <PatientPage schema={viewedDashboard.schema} doctorName={viewedDashboard.doctorName} />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10 flex items-center gap-2" style={{ color: "var(--slate)" }}>
        <Loader2 size={16} className="animate-spin" /> Chargement de l'historique...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <button
        onClick={onBack}
        className="flex items-center gap-1.5 text-sm font-medium mb-6"
        style={{ color: "var(--slate)" }}
      >
        <ArrowLeft size={14} /> Retour à la liste
      </button>

      <h1 className="text-3xl mb-6" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Historique du patient
      </h1>

      {/* Note de suivi : continue le dossier existant plutôt que d'en recréer un nouveau */}
      <div
        className="rounded-xl border p-5 mb-8"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--slate)" }}>
          Ajouter une note de suivi
        </p>
        <form onSubmit={handleFollowUpSubmit}>
          <textarea
            value={followUpNote}
            onChange={(e) => setFollowUpNote(e.target.value)}
            rows={4}
            placeholder="Ex : Contrôle de suivi, tension stabilisée à 13/8, poursuite du traitement..."
            className="w-full rounded-lg border p-3 text-sm resize-none focus:outline-none mb-3"
            style={{ borderColor: "var(--border)", color: "var(--ink)" }}
          />
          <button
            type="submit"
            disabled={continueMutation.isPending || followUpNote.trim().length === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition hover:brightness-110"
            style={{ background: "var(--sage)" }}
          >
            {continueMutation.isPending ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
            {continueMutation.isPending ? "Mise à jour en cours..." : "Mettre à jour le dossier"}
          </button>
          {continueMutation.isError && (
            <p className="text-sm mt-2" style={{ color: "var(--clay)" }}>
              {isAxiosError(continueMutation.error) && typeof continueMutation.error.response?.data?.detail === "string"
                ? continueMutation.error.response.data.detail
                : "Impossible de générer la mise à jour."}
            </p>
          )}
        </form>
      </div>

      {goalLabels.length > 0 && (
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: "var(--slate)" }}>
            Évolution d'un objectif clinique
          </p>
          <div className="flex gap-2 mb-4 flex-wrap">
            {goalLabels.map((label) => (
              <button
                key={label}
                onClick={() => setSelectedGoal(label)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium border"
                style={{
                  borderColor: "var(--border)",
                  background: selectedGoal === label ? "var(--sage-soft)" : "transparent",
                  color: selectedGoal === label ? "var(--sage-deep)" : "var(--slate)",
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {trend && trend.length > 0 && (
            <div
              className="rounded-xl border p-4"
              style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
            >
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(d) => new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" })}
                    fontSize={11}
                    stroke="var(--slate)"
                  />
                  <YAxis fontSize={11} stroke="var(--slate)" />
                  <Tooltip
                    labelFormatter={(d) => new Date(d).toLocaleDateString("fr-FR")}
                    formatter={(value: number, name: string) => [`${value}${trend[0]?.unit ?? ""}`, name]}
                  />
                  <Line type="monotone" dataKey="current_value" name="Valeur" stroke="var(--sage)" strokeWidth={2} />
                  <Line
                    type="monotone"
                    dataKey="target_value"
                    name="Objectif"
                    stroke="var(--amber)"
                    strokeDasharray="4 4"
                    strokeWidth={1.5}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--slate)" }}>
        Consultations ({consultations?.length ?? 0})
      </p>
      <div className="flex flex-col gap-3">
        {consultations?.slice().reverse().map((c) => (
          <button
            key={c.id}
            onClick={() => viewMutation.mutate(c.id)}
            className="text-left rounded-xl border p-4 transition hover:bg-black/[0.02]"
            style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <Calendar size={14} style={{ color: "var(--sage)" }} />
                <p className="text-xs font-mono" style={{ color: "var(--slate)" }}>
                  {new Date(c.created_at).toLocaleDateString("fr-FR", {
                    day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit",
                  })}
                </p>
              </div>
              {c.doctor_name && (
                <div className="flex items-center gap-1 text-xs" style={{ color: "var(--slate)" }}>
                  <Stethoscope size={12} /> {c.doctor_name}
                </div>
              )}
            </div>
            {c.diagnostics.length > 0 && (
              <p className="text-sm" style={{ color: "var(--ink)" }}>
                {c.diagnostics.join(", ")}
              </p>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
