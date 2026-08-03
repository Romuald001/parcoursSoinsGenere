import { motion } from "framer-motion";

/** Tracé façon électrocardiogramme, qui se dessine une fois à l'arrivée
 * sur la page. Motif propre au domaine de la santé — pas un effet générique. */
export default function VitalLine() {
  return (
    <svg viewBox="0 0 400 40" className="w-full h-10 mb-2" preserveAspectRatio="none">
      <motion.path
        d="M0 20 H140 L155 5 L170 35 L185 20 H400"
        fill="none"
        stroke="var(--sage)"
        strokeWidth="2"
        strokeLinecap="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 1.4, ease: "easeInOut" }}
      />
    </svg>
  );
}
