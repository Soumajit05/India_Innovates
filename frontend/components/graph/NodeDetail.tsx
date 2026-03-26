import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import type { GraphNode } from "@/lib/types";

export function NodeDetail({ node }: { node: GraphNode | null }) {
  if (!node) {
    return (
      <div className="panel p-5">
        <p className="panel-title">Node Detail</p>
        <p className="mt-4 text-sm leading-6 text-slate-400">Select a node to inspect its properties, domain, and connected intelligence pathways.</p>
      </div>
    );
  }

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="panel-title">{node.label}</p>
          <h3 className="mt-2 font-display text-2xl text-white">{node.name}</h3>
        </div>
        <ConfidenceBadge value={Math.min(1, node.connections / 10)} />
      </div>
      <div className="mt-5 space-y-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Domain</p>
          <p className="mt-2 text-lg text-white">{node.domain}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Connections</p>
          <p className="mt-2 text-lg text-white">{node.connections}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Properties</p>
          <pre className="mt-3 overflow-auto whitespace-pre-wrap font-mono text-xs leading-6 text-slate-300">
            {JSON.stringify(node.properties, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
