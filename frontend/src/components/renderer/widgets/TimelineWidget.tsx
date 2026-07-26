import { motion } from "framer-motion";
import type { TimelineWidgetData } from "../../../types/dashboardSchema";

function formatDate(iso?: string | null): string {
  if (!iso) return "Date à confirmer";
  const d = new Date(iso);
  return d.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: iso.includes("T") ? "2-digit" : undefined,
    minute: iso.includes("T") ? "2-digit" : undefined,
  });
}

export default function TimelineWidget({ events }: TimelineWidgetData) {
  return (
    <div
      className="card-elevate rounded-xl p-5 border"
      style={{ background: "var(--paper-raised)", borderColor: "var(--border)" }}
    >
      <ol className="relative border-l-2 pl-5 ml-1" style={{ borderColor: "var(--sage-soft)" }}>
        {events.map((event, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.08 }}
            className="mb-6 last:mb-0"
          >
            <span
              className="absolute -left-[7px] w-3 h-3 rounded-full ring-4"
              style={{ background: "var(--sage)", ["--tw-ring-color" as string]: "var(--paper-raised)" }}
            />
            <p className="text-sm font-medium" style={{ color: "var(--ink)" }}>
              {event.label}
            </p>
            <p className="text-xs font-mono mt-0.5" style={{ color: "var(--slate)" }}>
              {formatDate(event.date)}
              {event.status && ` · ${event.status}`}
            </p>
          </motion.li>
        ))}
      </ol>
    </div>
  );
}
