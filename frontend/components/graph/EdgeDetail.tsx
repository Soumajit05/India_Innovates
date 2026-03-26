import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { ProvenanceTag } from "@/components/shared/ProvenanceTag";
import type { GraphEdge } from "@/lib/types";

export function EdgeDetail({ edge }: { edge: GraphEdge | null }) {
  if (!edge) {
    return (
      <div className="panel p-5">
        <p className="panel-title">Edge Detail</p>
        <p className="mt-4 text-sm leading-6 text-slate-400">Select an edge to review relation type, confidence, provenance, and temporal strength.</p>
      </div>
    );
  }

  return (
    <div className="panel p-5">
      <div className="flex flex-wrap items-center gap-3">
        <span className="data-pill">{edge.type}</span>
        <ConfidenceBadge value={edge.current_strength} />
        <ProvenanceTag url={edge.source_url} />
      </div>
      <div className="mt-5 grid gap-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Current strength</p>
          <p className="mt-2 text-lg text-white">{edge.current_strength.toFixed(2)}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Decay rate</p>
          <p className="mt-2 text-lg text-white">{edge.decay_rate.toFixed(2)}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Tags</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {edge.tags.map((tag) => (
              <span key={tag} className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
