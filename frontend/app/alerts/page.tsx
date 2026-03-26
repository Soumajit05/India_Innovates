"use client";

import { useEffect, useState } from "react";

import { AlertFeed } from "../../components/alerts/AlertFeed";
import { Timeline } from "../../components/shared/Timeline";
import { CriticalityMap } from "../../components/shared/CriticalityMap";
import { getAlerts } from "../../lib/api";
import type { AlertItem } from "../../lib/types";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    void getAlerts().then(setAlerts);
  }, []);

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <AlertFeed alerts={alerts} />
      <div className="flex flex-col gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
          <div className="border-b border-slate-100 pb-4">
            <p className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Node Threat Topography</p>
            <h2 className="mt-1 text-xl font-bold text-[#212529]">Criticality Map</h2>
          </div>
          <div className="mt-6">
            <CriticalityMap />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
          <div className="border-b border-slate-100 pb-4">
            <p className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Escalation Timeline</p>
            <h2 className="mt-1 text-xl font-bold text-[#212529]">Analyst Prioritization Flow</h2>
          </div>
          <div className="mt-6">
            <Timeline
              items={alerts.map((alert) => ({
                title: alert.title,
                detail: alert.summary,
                meta: `${alert.domain} | severity ${Math.round(alert.severity * 100)}%`,
              }))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
