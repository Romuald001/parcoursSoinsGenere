import { motion } from "framer-motion";
import type { GoalProgressWidgetData } from "../../../types/dashboardSchema";

export default function GoalProgressWidget({
  label,
  current_value,
  target_value,
  unit,
  progress_percent,
}: GoalProgressWidgetData) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress_percent / 100) * circumference;

  return (
    <div
      className="card-elevate rounded-xl p-5 border flex items-center gap-5"
      style={{ background: "var(--paper-raised)", borderColor: "var(--border)" }}
    >
      <svg width="100" height="100" viewBox="0 0 100 100" className="shrink-0">
        <defs>
          <linearGradient id={`ring-${label}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--sage)" />
            <stop offset="100%" stopColor="var(--sage-deep)" />
          </linearGradient>
        </defs>
        <circle cx="50" cy="50" r={radius} fill="none" stroke="var(--sage-soft)" strokeWidth="8" />
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={`url(#ring-${label})`}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.15 }}
          transform="rotate(-90 50 50)"
        />
        <text
          x="50"
          y="55"
          textAnchor="middle"
          fontFamily="var(--font-mono)"
          fontSize="18"
          fill="var(--ink)"
        >
          {Math.round(progress_percent)}%
        </text>
      </svg>
      <div>
        <h3 className="text-base font-semibold" style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}>
          {label}
        </h3>
        <p className="text-sm font-mono mt-1" style={{ color: "var(--slate)" }}>
          {current_value}{unit} → objectif {target_value}{unit}
        </p>
      </div>
    </div>
  );
}
