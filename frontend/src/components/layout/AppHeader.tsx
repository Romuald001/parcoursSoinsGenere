import { Stethoscope, LogOut } from "lucide-react";
import { useAuth } from "../../context/useAuth";

export default function AppHeader() {
  const { token, logout } = useAuth();

  return (
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-2.5">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: "var(--sage)" }}
        >
          <Stethoscope size={18} color="#fff" />
        </div>
        <span
          className="text-sm font-semibold tracking-tight"
          style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}
        >
          Parcours de Soins
        </span>
      </div>
      {token && (
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-xs font-medium transition hover:opacity-70 print:hidden"
          style={{ color: "var(--slate)" }}
        >
          <LogOut size={13} />
          Se déconnecter
        </button>
      )}
    </div>
  );
}
