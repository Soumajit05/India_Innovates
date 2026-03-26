"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AlertFeed } from "../components/alerts/AlertFeed";
import { DomainMatrix } from "../components/dashboard/DomainMatrix";
import { IndiaMap } from "../components/dashboard/IndiaMap";
import { MetricCard } from "../components/dashboard/MetricCard";
import { ConfidenceBadge } from "../components/shared/ConfidenceBadge";
import { ProvenanceTag } from "../components/shared/ProvenanceTag";
import { getDashboardOverview } from "../lib/api";
import type { DashboardOverview } from "../lib/types";

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    void getDashboardOverview().then(setOverview);
  }, []);

  return (
    <>
      <section className="panel overflow-hidden px-6 py-8 md:px-8">
        <div className="grid gap-8 xl:grid-cols-[1.25fr_0.75fr]">
          <div>
            <p className="eyebrow">India-first strategic intelligence engine</p>
            <h1 className="mt-4 max-w-4xl font-display text-4xl leading-tight text-white md:text-6xl">
              A causal ontology for geopolitics, markets, climate, defense, and society.
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300">
              ARGOS fuses structured indicators and live open-source signals into a confidence-aware graph so analysts can move from question to grounded assessment in seconds.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/query" className="rounded-[22px] bg-gradient-to-r from-cyan-400 to-emerald-400 px-5 py-3 font-display text-sm uppercase tracking-[0.22em] text-slate-950">
                Launch Query Workbench
              </Link>
              <Link href="/graph" className="rounded-[22px] border border-white/10 px-5 py-3 text-sm text-slate-200 transition hover:border-cyan-400/35 hover:bg-white/5">
                Open Graph Explorer
              </Link>
            </div>
          </div>
          <div className="grid gap-3 rounded-[30px] border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between">
              <p className="panel-title">Mission Profile</p>
              <div className="data-pill">Graph-RAG active</div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
              <p className="font-display text-xl text-white">Top India exposures right now</p>
              <div className="mt-4 space-y-3">
                {overview?.top_vulnerabilities.map((citation) => (
                  <div key={citation.edge_id} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <ConfidenceBadge value={citation.strength} />
                      <ProvenanceTag url={citation.source_url} />
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-200">{citation.label}</p>
                  </div>
                )) ?? <p className="text-sm text-slate-400">Loading vulnerabilities...</p>}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {(overview?.metrics ?? []).map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} delta={metric.delta} />
        ))}
      </section>

      {overview ? (
        <>
          <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <DomainMatrix cells={overview.domain_matrix} />
            <IndiaMap states={overview.india_risk_overlay} />
          </section>
          <AlertFeed alerts={overview.alerts} />
        </>
      ) : null}
    </>
  );
}
