export interface TimelineItem {
  title: string;
  detail: string;
  meta?: string;
}

export function Timeline({ items }: { items: TimelineItem[] }) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div key={`${item.title}-${index}`} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className="h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_0_6px_rgba(34,211,238,0.12)]" />
            {index < items.length - 1 ? <div className="mt-2 h-full w-px bg-white/10" /> : null}
          </div>
          <div className="pb-4">
            <p className="font-display text-sm text-white">{item.title}</p>
            <p className="mt-1 text-sm leading-6 text-slate-300">{item.detail}</p>
            {item.meta ? <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.18em] text-slate-500">{item.meta}</p> : null}
          </div>
        </div>
      ))}
    </div>
  );
}
