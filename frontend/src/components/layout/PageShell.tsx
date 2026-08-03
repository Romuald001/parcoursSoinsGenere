import type { ReactNode } from "react";

/** Conteneur unique de mise en page : toute page vit dans cette largeur,
 * un seul endroit à modifier pour ajuster l'espacement du projet entier. */
export default function PageShell({ children }: { children: ReactNode }) {
  return <div className="max-w-6xl mx-auto px-6 py-10">{children}</div>;
}
