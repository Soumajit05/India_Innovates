import clsx from "clsx";

export function ConfidenceBadge({ value, className }: { value: number; className?: string }) {
  const tone =
    value >= 0.8
      ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-200"
      : value >= 0.5
        ? "border-amber-400/25 bg-amber-400/10 text-amber-100"
        : "border-rose-400/25 bg-rose-400/10 text-rose-100";

  return (
    <span className={clsx("inline-flex items-center rounded-full border px-2.5 py-1 font-mono text-[11px] uppercase tracking-[0.18em]", tone, className)}>
      {Math.round(value * 100)}% confidence
    </span>
  );
}
