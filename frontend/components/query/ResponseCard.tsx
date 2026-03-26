import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import type { QueryResponse } from "@/lib/types";

function BulletList({ items }: { items: string[] }) {
  if (!items.length) {
    return <p className="mt-3 text-sm leading-6 text-slate-400">No grounded items returned for this section yet.</p>;
  }

  return (
    <ul className="mt-3 space-y-3 text-sm leading-6 text-slate-200">
      {items.map((item) => (
        <li key={item} className="flex gap-3">
          <span className="mt-2 h-1.5 w-1.5 rounded-full bg-cyan-300" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function ResponseCard({ result }: { result: QueryResponse | null }) {
  if (!result) {
    return (
      <div className="panel p-5">
        <p className="panel-title">Latest Analysis</p>
        <p className="mt-4 text-sm leading-6 text-slate-400">
          Start a conversation above and ARGOS will keep the latest grounded brief, citations, and causal chain in sync.
        </p>
      </div>
    );
  }

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="panel-title">Latest Analysis</p>
          <h2 className="mt-2 font-display text-2xl text-white">Grounded Brief</h2>
        </div>
        <ConfidenceBadge value={result.brief.overall_confidence} />
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs uppercase tracking-[0.18em] text-slate-400">
        <span className="rounded-full border border-white/10 px-3 py-1">Query {result.query_id.slice(0, 8)}</span>
        <span className="rounded-full border border-white/10 px-3 py-1">{result.query_time_ms} ms</span>
        <span className="rounded-full border border-white/10 px-3 py-1">
          {Math.round((result.grounding_rate ?? 0) * 100)}% grounded
        </span>
        {result.llm_fallback_used ? (
          <span className="rounded-full border border-amber-400/30 px-3 py-1 text-amber-200">Fallback mode</span>
        ) : (
          <span className="rounded-full border border-emerald-400/30 px-3 py-1 text-emerald-200">Live AI synthesis</span>
        )}
      </div>

      <p className="mt-5 text-base leading-7 text-slate-100">{result.brief.strategic_assessment}</p>

      {result.warning ? (
        <div className="mt-4 rounded-[20px] border border-amber-400/20 bg-amber-400/10 p-3 text-sm text-amber-100">
          {result.warning}
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <section className="rounded-[24px] border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">Key Findings</p>
          <BulletList items={result.brief.key_findings} />
        </section>

        <section className="rounded-[24px] border border-white/10 bg-white/5 p-4">
          <p className="eyebrow">India Implications</p>
          <BulletList items={result.brief.india_implications} />
        </section>
      </div>

      <section className="mt-4 rounded-[24px] border border-white/10 bg-white/5 p-4">
        <p className="eyebrow">Risk Factors</p>
        <BulletList items={result.brief.risk_factors} />
      </section>
    </div>
  );
}
