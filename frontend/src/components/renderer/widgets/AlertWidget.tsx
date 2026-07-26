import { motion } from "framer-motion";
import { Info, AlertTriangle, AlertCircle } from "lucide-react";
import type { AlertWidgetData } from "../../../types/dashboardSchema";

const SEVERITY_STYLES = {
  info: { bg: "var(--info-soft)", fg: "var(--info)", label: "Information", Icon: Info },
  warning: { bg: "var(--amber-soft)", fg: "var(--amber)", label: "À vérifier", Icon: AlertTriangle },
  critical: { bg: "var(--clay-soft)", fg: "var(--clay)", label: "Important", Icon: AlertCircle },
};

export default function AlertWidget({ items }: AlertWidgetData) {
  return (
    <div className="flex flex-col gap-3">
      {items.map((item, i) => {
        const style = SEVERITY_STYLES[item.severity];
        const Icon = style.Icon;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
            className="rounded-xl p-4 border-l-4 flex items-start gap-3"
            style={{ background: style.bg, borderLeftColor: style.fg }}
          >
            <Icon size={16} color={style.fg} className="shrink-0 mt-0.5" />
            <div>
              <span
                className="text-xs font-semibold uppercase tracking-wide block mb-0.5"
                style={{ color: style.fg }}
              >
                {style.label}
              </span>
              <p className="text-sm" style={{ color: "var(--ink)" }}>
                {item.message}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
