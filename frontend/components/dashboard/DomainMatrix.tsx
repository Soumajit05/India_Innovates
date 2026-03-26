import type { DomainMatrixCell } from "@/lib/types";

const domains = ["Geopolitics", "Economics", "Defense", "Technology", "Climate", "Society"] as const;

export function DomainMatrix({ cells }: { cells: DomainMatrixCell[] }) {
  const valueFor = (from: string, to: string) => cells.find((cell) => cell.from_domain === from && cell.to_domain === to)?.value ?? 0;

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-title">Cross-Domain Heat Map</p>
          <h2 className="mt-2 font-display text-2xl text-white">Causal Density Matrix</h2>
        </div>
        <div className="data-pill">live graph crossovers</div>
      </div>
      <div className="mt-6 overflow-x-auto">
        <div className="grid min-w-[700px] grid-cols-[140px_repeat(6,minmax(84px,1fr))] gap-2">
          <div />
          {domains.map((domain) => (
            <div key={domain} className="eyebrow text-center">
              {domain}
            </div>
          ))}
          {domains.map((fromDomain) => (
            <div key={fromDomain} className="contents">
              <div className="flex items-center font-display text-sm text-slate-200">{fromDomain}</div>
              {domains.map((toDomain) => {
                const value = valueFor(fromDomain, toDomain);
                const glow = Math.min(value / 8, 1);
                return (
                  <div
                    key={`${fromDomain}-${toDomain}`}
                    className="flex h-20 items-center justify-center rounded-2xl border border-white/8 text-lg font-display text-white"
                    style={{
                      background: `linear-gradient(180deg, rgba(53,208,170,${0.08 + glow * 0.22}), rgba(247,184,75,${glow * 0.14}))`,
                    }}
                  >
                    {value}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
