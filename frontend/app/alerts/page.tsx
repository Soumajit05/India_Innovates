"use client";

import { useEffect, useState } from "react";

import { AlertFeed } from "../../components/alerts/AlertFeed";
import { Timeline } from "../../components/shared/Timeline";
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
      <div className="panel p-5">
        <div>
          <p className="panel-title">Escalation Timeline</p>
          <h2 className="mt-2 font-display text-2xl text-white">Analyst Prioritization Flow</h2>
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
  );
}
