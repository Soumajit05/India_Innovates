import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { ProvenanceTag } from "@/components/shared/ProvenanceTag";
import type { AlertItem } from "@/lib/types";

export function AlertCard({ alert }: { alert: AlertItem }) {
  return (
    <article className="rounded-[24px] border border-white/10 bg-white/5 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className="data-pill">{alert.domain}</span>
        <ConfidenceBadge value={alert.severity} />
        <ProvenanceTag url={alert.source_url} />
      </div>
      <h3 className="mt-4 font-display text-xl text-white">{alert.title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-300">{alert.summary}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {alert.affected_entities.map((entity) => (
          <span key={entity} className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">
            {entity}
          </span>
        ))}
      </div>
    </article>
  );
}
