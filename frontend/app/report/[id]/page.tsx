import Link from "next/link";

export default function ReportPage({ params }: { params: { id: string } }) {
  const title = params.id
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return (
    <div className="panel max-w-5xl p-8">
      <p className="eyebrow">Strategic Report</p>
      <h1 className="mt-3 font-display text-4xl text-white">{title}</h1>
      <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300">
        This route is reserved for generated strategic briefs. As the backend evolves from in-memory storage to persistent report generation, this page can render archived query outputs, scenario packages, and judge-demo snapshots.
      </p>
      <div className="mt-8 rounded-[26px] border border-white/10 bg-white/5 p-6">
        <p className="panel-title">Suggested Sections</p>
        <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-200">
          <li>• Strategic assessment with overall confidence</li>
          <li>• Key findings and contradiction handling</li>
          <li>• India implications and vulnerable sectors</li>
          <li>• Evidence appendix with source provenance</li>
        </ul>
      </div>
      <Link href="/query" className="mt-8 inline-flex rounded-[22px] border border-white/10 px-5 py-3 text-sm text-slate-200 transition hover:border-cyan-400/35 hover:bg-white/5">
        Return to Query Workbench
      </Link>
    </div>
  );
}
