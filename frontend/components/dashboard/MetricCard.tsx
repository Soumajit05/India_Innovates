export function MetricCard({ label, value, delta }: { label: string; value: string; delta: string }) {
  return (
    <div className="panel relative overflow-hidden px-5 py-5">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent" />
      <p className="panel-title">{label}</p>
      <div className="mt-4 flex items-end justify-between gap-3">
        <p className="font-display text-4xl tracking-tight text-white">{value}</p>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cyan-200">{delta}</p>
      </div>
    </div>
  );
}
