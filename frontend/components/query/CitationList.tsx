import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { ProvenanceTag } from "@/components/shared/ProvenanceTag";
import type { Citation } from "@/lib/types";

export function CitationList({ citations }: { citations: Citation[] }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-title">Evidence</p>
          <h2 className="mt-2 font-display text-2xl text-white">Cited Graph Edges</h2>
        </div>
        <div className="data-pill">{citations.length} citations</div>
      </div>
      <div className="mt-6 space-y-3">
        {citations.map((citation) => (
          <a key={citation.edge_id} href={citation.source_url} target="_blank" rel="noreferrer" className="block rounded-[22px] border border-white/10 bg-white/5 p-4 transition hover:border-cyan-400/30">
            <div className="flex flex-wrap items-center gap-3">
              <ConfidenceBadge value={citation.strength} />
              <ProvenanceTag url={citation.source_url} />
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-100">{citation.label}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
