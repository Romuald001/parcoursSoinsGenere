import { useQuery } from "@tanstack/react-query";
import { Users, ChevronRight, Loader2 } from "lucide-react";
import { listPatients } from "../api/client";

interface Props {
  onSelectPatient: (patientId: string) => void;
}

export default function PatientListPage({ onSelectPatient }: Props) {
  const { data: patients, isLoading } = useQuery({
    queryKey: ["patients"],
    queryFn: listPatients,
  });

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10 flex items-center gap-2" style={{ color: "var(--slate)" }}>
        <Loader2 size={16} className="animate-spin" /> Chargement des patients...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <p className="text-sm font-mono" style={{ color: "var(--sage)" }}>
        {patients?.length ?? 0} patient(s) suivi(s)
      </p>
      <h1 className="text-3xl mt-1 mb-6" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Mes patients
      </h1>

      {(!patients || patients.length === 0) && (
        <p className="text-sm" style={{ color: "var(--slate)" }}>
          Aucun patient pour le moment. Lancez une nouvelle consultation pour en créer un.
        </p>
      )}

      <div
        className="rounded-xl border divide-y"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        {patients?.map((p) => (
          <button
            key={p.id}
            onClick={() => onSelectPatient(p.id)}
            className="w-full flex items-center justify-between gap-3 p-4 text-left transition hover:bg-black/[0.02]"
          >
            <div className="flex items-center gap-3">
              <Users size={16} style={{ color: "var(--sage)" }} />
              <div>
                <p className="text-sm font-medium" style={{ color: "var(--ink)" }}>{p.full_name}</p>
                <p className="text-xs font-mono" style={{ color: "var(--slate)" }}>
                  Né(e) le {p.birth_date} · {p.consultation_count} consultation(s)
                </p>
              </div>
            </div>
            <ChevronRight size={16} style={{ color: "var(--slate)" }} />
          </button>
        ))}
      </div>
    </div>
  );
}
