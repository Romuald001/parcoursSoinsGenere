import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Users, ChevronRight, Loader2, Search } from "lucide-react";
import { listPatients } from "../api/client";
import PageShell from "../components/layout/PageShell";

interface Props {
  onSelectPatient: (patientId: string) => void;
}

type Filter = "mine" | "all";

export default function PatientListPage({ onSelectPatient }: Props) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("mine");

  const { data: patients, isLoading } = useQuery({
    queryKey: ["patients"],
    queryFn: listPatients,
  });

  const filteredPatients = useMemo(() => {
    if (!patients) return [];
    const bySearch = patients.filter((p) =>
      p.full_name.toLowerCase().includes(search.trim().toLowerCase())
    );
    if (filter === "mine") {
      return bySearch.filter((p) => p.consulted_by_me);
    }
    return bySearch;
  }, [patients, search, filter]);

  const mineCount = patients?.filter((p) => p.consulted_by_me).length ?? 0;

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10 flex items-center gap-2" style={{ color: "var(--slate)" }}>
        <Loader2 size={16} className="animate-spin" /> Chargement des patients...
      </div>
    );
  }

  return (
    <PageShell>
      <p className="text-sm font-mono" style={{ color: "var(--sage)" }}>
        {filteredPatients.length} patient(s) affiché(s)
      </p>
      <h1 className="text-3xl mt-1 mb-6" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Mes patients
      </h1>

      {/* Recherche par nom */}
      <div
        className="flex items-center gap-2 px-3 py-2 rounded-lg border mb-3"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        <Search size={15} style={{ color: "var(--slate)" }} />
        <input
          type="text"
          placeholder="Rechercher un patient par nom..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 text-sm focus:outline-none bg-transparent"
          style={{ color: "var(--ink)" }}
        />
      </div>

      {/* Filtre Mes patients / Tous les patients */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter("mine")}
          className="px-3 py-1.5 rounded-lg text-xs font-medium border"
          style={{
            borderColor: "var(--border)",
            background: filter === "mine" ? "var(--sage-soft)" : "transparent",
            color: filter === "mine" ? "var(--sage-deep)" : "var(--slate)",
          }}
        >
          Mes patients ({mineCount})
        </button>
        <button
          onClick={() => setFilter("all")}
          className="px-3 py-1.5 rounded-lg text-xs font-medium border"
          style={{
            borderColor: "var(--border)",
            background: filter === "all" ? "var(--sage-soft)" : "transparent",
            color: filter === "all" ? "var(--sage-deep)" : "var(--slate)",
          }}
        >
          Tous les patients ({patients?.length ?? 0})
        </button>
      </div>

      {filteredPatients.length === 0 && (
        <p className="text-sm" style={{ color: "var(--slate)" }}>
          {search
            ? "Aucun patient ne correspond à cette recherche."
            : filter === "mine"
            ? "Vous n'avez pas encore consulté de patient. Essayez l'onglet 'Tous les patients' pour la continuité de soins."
            : "Aucun patient pour le moment."}
        </p>
      )}

      <div
        className="rounded-xl border divide-y"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        {filteredPatients.map((p) => (
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
    </PageShell>
  );
}
