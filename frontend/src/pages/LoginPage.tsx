import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { LogIn, Loader2 } from "lucide-react";
import { isAxiosError } from "axios";
import AppHeader from "../components/layout/AppHeader";
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
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-md mx-auto px-4 py-16"
    >
      <AppHeader />
      <h1 className="text-3xl mb-2" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
        Connexion
      </h1>
      <p className="text-sm mb-6" style={{ color: "var(--slate)" }}>
        Accédez à votre espace avec votre email ou votre numéro de téléphone.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
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
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white disabled:opacity-40 transition hover:brightness-110"
          style={{ background: "var(--sage)" }}
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <LogIn size={15} />}
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>

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
  );
}
