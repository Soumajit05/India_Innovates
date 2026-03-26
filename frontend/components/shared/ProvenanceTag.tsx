export function ProvenanceTag({ url }: { url: string }) {
  let hostname = url;
  try {
    hostname = new URL(url).hostname.replace("www.", "");
  } catch {
    hostname = url;
  }

  return (
    <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.14em] text-slate-300">
      {hostname}
    </span>
  );
}
