import { motion } from "framer-motion";
import type { DashboardSchema } from "../../types/dashboardSchema";
import { widgetRegistry } from "./widgetRegistry";

interface Props {
  schema: DashboardSchema;
}

function SectionBlock({ section, index }: { section: DashboardSchema["sections"][number]; index: number }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.06 }}
    >
      <h2
        className="text-xs font-semibold uppercase tracking-wider mb-3"
        style={{ color: "var(--slate)" }}
      >
        {section.title}
      </h2>
      <div className="flex flex-col gap-4">
        {section.widgets.map((widget) => {
          const Component = widgetRegistry[widget.type];
          if (!Component) {
            console.warn(`Aucun composant enregistré pour le type "${widget.type}"`);
            return null;
          }
          return <Component key={widget.id} {...widget} />;
        })}
      </div>
    </motion.section>
  );
}

export default function DashboardRenderer({ schema }: Props) {
  const [firstSection, ...otherSections] = schema.sections;

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <motion.header
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-8"
      >
        <p className="text-sm font-mono" style={{ color: "var(--sage)" }}>
          {schema.patient_header.greeting}
        </p>
        <h1
          className="text-3xl mt-1"
          style={{ fontFamily: "var(--font-display)", color: "var(--ink)" }}
        >
          {schema.patient_header.full_name}
          <span className="text-lg font-mono ml-3" style={{ color: "var(--slate)" }}>
            {schema.patient_header.age} ans
          </span>
        </h1>
      </motion.header>

      {/* Première section (résumé) en pleine largeur, comme un en-tête éditorial */}
      {firstSection && (
        <div className="mb-8">
          <SectionBlock section={firstSection} index={0} />
        </div>
      )}

      {/* Sections suivantes en colonnes façon "mur de cartes" */}
      {otherSections.length > 0 && (
        <div className="columns-1 md:columns-2 xl:columns-3 gap-6 print-columns-1">
          {otherSections.map((section, i) => (
            <div key={i} className="break-inside-avoid mb-6">
              <SectionBlock section={section} index={i + 1} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
