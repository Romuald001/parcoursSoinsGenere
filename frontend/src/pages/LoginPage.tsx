import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { LogIn, Loader2 } from "lucide-react";
import { isAxiosError } from "axios";
import AppHeader from "../components/layout/AppHeader";
import PageShell from "../components/layout/PageShell";
import VitalLine from "../components/layout/VitalLine";
import { useAuth } from "../context/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(identifier, password);
    } catch (err: unknown) {
      const message =
        isAxiosError(err) && typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : "Connexion impossible. Vérifiez vos identifiants.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageShell>
      <AppHeader />
      <div className="max-w-md mx-auto mt-10">
        <VitalLine />
        <motion.h1
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
          className="text-3xl mb-2"
          style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}
        >
          Connexion
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-sm mb-6"
          style={{ color: "var(--slate)" }}
        >
          Accédez à votre espace avec votre email ou votre numéro de téléphone.
        </motion.p>

        <motion.form
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          onSubmit={handleSubmit}
          className="flex flex-col gap-3"
        >
          <input
            type="text"
            required
            placeholder="Email ou numéro de téléphone"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            className="px-4 py-2.5 rounded-lg border text-sm focus:outline-none"
            style={{ borderColor: "var(--border)", background: "var(--paper-raised)", color: "var(--ink)" }}
          />
          <input
            type="password"
            required
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="px-4 py-2.5 rounded-lg border text-sm focus:outline-none"
            style={{ borderColor: "var(--border)", background: "var(--paper-raised)", color: "var(--ink)" }}
          />
          <motion.button
            type="submit"
            disabled={loading}
            animate={loading ? {} : { scale: [1, 1.02, 1] }}
            transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white disabled:opacity-40"
            style={{ background: "var(--sage)" }}
          >
            {loading ? <Loader2 size={15} className="animate-spin" /> : <LogIn size={15} />}
            {loading ? "Connexion..." : "Se connecter"}
          </motion.button>
        </motion.form>

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
      </div>
    </PageShell>
  );
}
