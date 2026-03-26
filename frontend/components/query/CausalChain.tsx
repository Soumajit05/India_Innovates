import { Timeline } from "@/components/shared/Timeline";
import type { QueryResponse } from "@/lib/types";

export function CausalChain({ result }: { result: QueryResponse | null }) {
  if (!result?.causal_chain) {
    return (
      <div className="panel p-5">
        <p className="panel-title">Causal Chain</p>
        <p className="mt-4 text-sm leading-6 text-slate-400">When the query resolves to a strong path, ARGOS will map hop-by-hop causal propagation here.</p>
      </div>
    );
  }

  const chain = result.causal_chain;
  const items = chain.path.map((step, index) => ({
    title: step,
    detail: index % 2 === 0 ? "Node in the retrieved chain." : "Typed relationship connecting the surrounding nodes.",
    meta: index === chain.path.length - 1 ? `${chain.time_to_impact_days} days` : undefined,
  }));

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-title">Causal Chain</p>
          <h2 className="mt-2 font-display text-2xl text-white">Confidence-Weighted Path</h2>
        </div>
        <div className="data-pill">{Math.round(chain.chain_confidence * 100)}% chain confidence</div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-300">{chain.explanation}</p>
      {chain.warnings?.length ? (
        <div className="mt-4 rounded-[20px] border border-amber-400/20 bg-amber-400/10 p-3 text-sm text-amber-100">
          {chain.warnings.join(" ")}
        </div>
      ) : null}
      <div className="mt-6">
        <Timeline items={items} />
      </div>
    </div>
  );
}
