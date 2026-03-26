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
    <div className="space-y-6">
      <section className="bg-white shadow-sm rounded-lg p-6 md:p-8 border border-slate-200">
        <div className="grid gap-8 xl:grid-cols-[1.25fr_0.75fr]">
          <div className="flex flex-col justify-center">
            <p className="text-sm font-bold tracking-wider text-[#0056B3] uppercase">India-first Strategic Intelligence</p>
            <h1 className="mt-4 max-w-4xl text-3xl font-bold leading-tight text-[#212529] md:text-5xl">
              Causal Ontology for Geopolitics, Markets, Climate, Defense, and Society.
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-slate-600">
              ARGOS fuses structured indicators and live open-source signals into a confidence-aware graph so analysts can move from question to grounded assessment in seconds.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link href="/query" className="rounded-md bg-[#0056B3] hover:bg-[#004494] px-6 py-3 font-semibold text-white transition-colors shadow-sm">
                Launch Query Workbench
              </Link>
              <Link href="/graph" className="rounded-md bg-white border border-[#0056B3] text-[#0056B3] hover:bg-slate-50 px-6 py-3 font-semibold transition-colors shadow-sm">
                Open Graph Explorer
              </Link>
            </div>
          </div>
          <div className="grid gap-4 rounded-lg border border-slate-200 bg-slate-50 p-6 flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-2">
              <h2 className="text-lg font-bold text-[#212529]">Mission Profile</h2>
              <span className="px-3 py-1 bg-[#28A745]/10 text-[#28A745] text-xs font-bold rounded uppercase tracking-wide border border-[#28A745]/30">Active</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-[#003366] mb-4">Top India Exposures</h3>
              <div className="space-y-4">
                {overview?.top_vulnerabilities.map((citation) => (
                  <div key={citation.edge_id} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex flex-wrap items-center gap-3">
                      <ConfidenceBadge value={citation.strength} />
                      <ProvenanceTag url={citation.source_url} />
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-slate-700 font-medium">{citation.label}</p>
                  </div>
                )) ?? <p className="text-sm text-slate-500 italic">Synchronizing vulnerability feeds...</p>}
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
          <div className="bg-white shadow-sm rounded-lg border border-slate-200 overflow-hidden">
             <AlertFeed alerts={overview.alerts} />
          </div>
        </>
      ) : null}
    </div>
  );
}
