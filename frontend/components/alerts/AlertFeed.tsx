import type { AlertItem } from "@/lib/types";

import { AlertCard } from "@/components/alerts/AlertCard";

export function AlertFeed({ alerts }: { alerts: AlertItem[] }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-title">Live Alerts</p>
          <h2 className="mt-2 font-display text-2xl text-white">Operational Watchlist</h2>
        </div>
        <div className="data-pill">{alerts.length} active items</div>
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
}
