import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { isAxiosError } from "axios";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UserPlus, Stethoscope, Loader2 } from "lucide-react";
import AppHeader from "../components/layout/AppHeader";
import { registerDoctor, listDoctors } from "../api/client";

export default function AdminDashboardPage() {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // React Query gère lui-même le fetch au montage, le cache et les re-fetch :
  // plus besoin d'un useEffect manuel qui appellerait setState.
  const { data: doctors = [] } = useQuery({
    queryKey: ["doctors"],
    queryFn: listDoctors,
  });

  const mutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      registerDoctor(email, password),
    onSuccess: () => {
      setSuccess(`Compte créé pour ${email}.`);
      setEmail("");
      setPassword("");
      queryClient.invalidateQueries({ queryKey: ["doctors"] });
    },
    onError: (err: unknown) => {
      const message =
        isAxiosError(err) && typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : "Impossible de créer ce compte.";
      setError(message);
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    mutation.mutate({ email, password });
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-2xl mx-auto px-4 py-10"
    >
      <AppHeader />
      <p className="text-sm font-mono" style={{ color: "var(--sage)" }}>
        Espace administrateur
      </p>
      <h1 className="text-3xl mt-1 mb-6" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Gestion des médecins
      </h1>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl p-5 border mb-8"
        style={{ background: "var(--paper-raised)", borderColor: "var(--border)" }}
      >
        <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--slate)" }}>
          Créer un compte médecin
        </p>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="email"
            required
            placeholder="Email du médecin"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
        </div>
        {error && <p className="text-sm mt-3" style={{ color: "var(--clay)" }}>{error}</p>}
        {success && <p className="text-sm mt-3" style={{ color: "var(--sage)" }}>{success}</p>}
      </form>

      <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--slate)" }}>
        Médecins ({doctors.length})
      </p>
      <div
        className="rounded-xl border divide-y"
        style={{ borderColor: "var(--border)", background: "var(--paper-raised)" }}
      >
        {doctors.length === 0 && (
          <p className="text-sm p-4" style={{ color: "var(--slate)" }}>
            Aucun médecin enregistré pour le moment.
          </p>
        )}
        {doctors.map((d) => (
          <div key={d.id} className="flex items-center gap-3 p-4">
            <Stethoscope size={16} style={{ color: "var(--sage)" }} />
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--ink)" }}>{d.email}</p>
              <p className="text-xs font-mono" style={{ color: "var(--slate)" }}>
                Créé le {new Date(d.created_at).toLocaleDateString("fr-FR")}
              </p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
