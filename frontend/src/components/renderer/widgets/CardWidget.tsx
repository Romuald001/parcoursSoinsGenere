import { motion } from "framer-motion";
import type { CardWidgetData } from "../../../types/dashboardSchema";

export default function CardWidget({ title, subtitle, description, confidence_badge }: CardWidgetData) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="card-elevate rounded-xl p-5 border"
      style={{ background: "var(--paper-raised)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between gap-3">
        <h3
          className="text-lg font-semibold"
          style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}
        >
          {title}
        </h3>
        {confidence_badge != null && (
          <span
            className="text-xs px-2 py-1 rounded-full font-mono shrink-0"
            style={{ background: "var(--amber-soft)", color: "var(--amber)" }}
            title="Information déduite avec une certitude partielle, à vérifier"
          >
            {Math.round(confidence_badge * 100)}% sûr
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-sm mt-1 font-mono" style={{ color: "var(--slate)" }}>
          {subtitle}
        </p>
      )}
      {description && (
        <p className="text-sm mt-3 leading-relaxed" style={{ color: "var(--ink)" }}>
          {description}
        </p>
      )}
    </motion.div>
  );
}
