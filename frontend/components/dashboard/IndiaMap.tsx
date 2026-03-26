import type { IndiaRiskState } from "@/lib/types";

export function IndiaMap({ states }: { states: IndiaRiskState[] }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-title">India Overlay</p>
          <h2 className="mt-2 font-display text-2xl text-white">Strategic Risk Gradient</h2>
        </div>
        <div className="data-pill">state-level pulse</div>
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="relative min-h-[320px] rounded-[28px] border border-white/10 bg-gradient-to-br from-slate-900 via-slate-950 to-cyan-950/40">
          <div className="absolute left-[34%] top-[10%] h-[58%] w-[34%] rounded-[48%_42%_54%_40%] border border-cyan-400/20 bg-cyan-400/5 shadow-[inset_0_0_40px_rgba(14,165,233,0.08)]" />
          {states.map((state, index) => (
            <div
              key={state.state}
              className="absolute flex items-center gap-2"
              style={{
                left: `${38 + (index % 2) * 18}%`,
                top: `${18 + index * 13}%`,
              }}
            >
              <span
                className="h-3.5 w-3.5 rounded-full"
                style={{ background: `rgba(255, 122, 89, ${Math.min(state.score / 100, 1)})` }}
              />
              <span className="rounded-full border border-white/10 bg-black/45 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.16em] text-slate-200">
                {state.state}
              </span>
            </div>
          ))}
        </div>
        <div className="space-y-3">
          {states.map((state) => (
            <div key={state.state} className="rounded-[24px] border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-display text-lg text-white">{state.state}</p>
                <p className="font-mono text-xs uppercase tracking-[0.18em] text-orange-200">{state.score}/100</p>
              </div>
              <div className="mt-3 h-2 rounded-full bg-white/5">
                <div className="h-2 rounded-full bg-gradient-to-r from-amber-300 via-orange-400 to-rose-500" style={{ width: `${state.score}%` }} />
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-300">{state.driver}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
