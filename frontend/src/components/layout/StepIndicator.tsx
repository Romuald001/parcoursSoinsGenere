import { Check, FileText, ScanSearch, LayoutDashboard } from "lucide-react";

type Step = "doctor" | "model" | "patient";

const STEPS: { key: Step; label: string; icon: typeof FileText }[] = [
  { key: "doctor", label: "Note", icon: FileText },
  { key: "model", label: "Dossier", icon: ScanSearch },
  { key: "patient", label: "Tableau de bord", icon: LayoutDashboard },
];

export default function StepIndicator({ current }: { current: Step }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="flex items-center gap-2 mb-10">
      {STEPS.map((step, i) => {
        const isDone = i < currentIndex;
        const isActive = i === currentIndex;
        const Icon = step.icon;

        return (
          <div key={step.key} className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-300"
                style={{
                  background: isDone || isActive ? "var(--sage)" : "var(--sage-soft)",
                  color: isDone || isActive ? "#fff" : "var(--slate)",
                }}
              >
                {isDone ? <Check size={15} /> : <Icon size={15} />}
              </div>
              <span
                className="text-xs font-medium hidden sm:inline"
                style={{ color: isActive ? "var(--ink)" : "var(--slate)" }}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className="w-8 h-px mx-1"
                style={{ background: isDone ? "var(--sage)" : "var(--border)" }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
