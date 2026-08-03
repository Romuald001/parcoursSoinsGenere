import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Loader2 } from "lucide-react";
import StepIndicator from "../components/layout/StepIndicator";
import PageShell from "../components/layout/PageShell";

interface Props {
  onSubmit: (rawNote: string) => void;
  loading: boolean;
  error: string | null;
}

const EXAMPLE_NOTE = `Patient: Marie Lambert, née le 14/03/1965, sexe féminin, niveau de compréhension médicale faible.
Suivie pour un diabète de type 2 diagnostiqué il y a 3 ans, assez bien contrôlé.
Actuellement sous Metformine 850mg, 2 fois par jour.
Se plaint de fatigue modérée depuis 2 semaines.
Prochain rendez-vous de suivi prévu le 15 septembre 2026 à 10h, cabinet du Dr Martin.
Objectif : ramener l'HbA1c sous 7%, actuellement à 7.8%.`;

export default function DoctorPage({ onSubmit, loading, error }: Props) {
  const [note, setNote] = useState("");

  return (
    <PageShell>
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-6xl mx-auto"
    >
      <StepIndicator current="doctor" />

      <h1
        className="text-3xl mb-2"
        style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}
      >
        Notes de consultation
      </h1>
      <p className="text-sm mb-6" style={{ color: "var(--slate)" }}>
        Rédigez la note comme vous le feriez habituellement. Le système
        s'occupe de structurer l'information et de préparer le tableau de
        bord du patient.
      </p>

      <div
        className="rounded-xl border overflow-hidden transition-shadow focus-within:shadow-md"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={10}
          placeholder="Ex : Patient suivi pour hypertension, tension à 15/9, sous Amlodipine 5mg..."
          className="w-full p-4 text-sm resize-none focus:outline-none"
          style={{ color: "var(--ink)", fontFamily: "var(--font-body)" }}
        />
      </div>

      <div className="flex items-center gap-3 mt-4">
        <button
          onClick={() => onSubmit(note)}
          disabled={loading || note.trim().length === 0}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition hover:brightness-110"
          style={{ background: "var(--sage)" }}
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
          {loading ? "Analyse en cours..." : "Générer le dossier du patient"}
        </button>
        <button
          onClick={() => setNote(EXAMPLE_NOTE)}
          disabled={loading}
          className="px-4 py-2.5 rounded-lg text-sm font-medium border disabled:opacity-40 transition hover:bg-black/[0.02]"
          style={{ borderColor: "var(--border)", color: "var(--slate)" }}
        >
          Remplir avec un exemple
        </button>
      </div>

      {error && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 text-sm rounded-lg p-3"
          style={{ background: "var(--clay-soft)", color: "var(--clay)" }}
        >
          {error}
        </motion.p>
      )}
    </motion.div>
    </PageShell>
  );
}
