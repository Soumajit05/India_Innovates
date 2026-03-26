"use client";
import { useState } from "react";
import type { AlertItem } from "@/lib/types";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { ProvenanceTag } from "@/components/shared/ProvenanceTag";

export function AlertFeed({ alerts }: { alerts: AlertItem[] }) {
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);

  const severityColor = (sev: number) => {
    if (sev >= 0.8) return "bg-red-100 text-red-800 border-red-300";
    if (sev >= 0.5) return "bg-yellow-100 text-yellow-800 border-yellow-300";
    return "bg-green-100 text-green-800 border-green-300";
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="flex items-center justify-between p-5 border-b border-slate-200 bg-[#F4F6F9]">
          <div>
            <span className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Operational Watchlist</span>
            <h2 className="mt-1 text-xl font-bold text-[#212529]">Live Alerts</h2>
          </div>
          <div className="px-3 py-1 bg-[#152A38] text-white text-xs font-bold rounded">
            {alerts.length} Active Items
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-700">
            <thead className="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-6 py-3 font-semibold text-[#003366]">Timestamp / Domain</th>
                <th scope="col" className="px-6 py-3 font-semibold text-[#003366]">Severity</th>
                <th scope="col" className="px-6 py-3 font-semibold text-[#003366]">Title & Summary</th>
                <th scope="col" className="px-6 py-3 font-semibold text-[#003366]">Entities</th>
                <th scope="col" className="px-6 py-3 font-semibold text-[#003366] text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert, idx) => (
                <tr key={alert.id} className={`border-b border-slate-200 hover:bg-slate-50 transition-colors ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-semibold block">{alert.domain}</span>
                    <span className="text-xs text-slate-500">{new Date().toISOString().split('T')[0]}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium border ${severityColor(alert.severity)}`}>
                      {(alert.severity * 100).toFixed(0)}%
                    </div>
                  </td>
                  <td className="px-6 py-4 max-w-md">
                    <p className="font-semibold text-slate-900 mb-1">{alert.title}</p>
                    <p className="text-xs text-slate-600 truncate">{alert.summary}</p>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {alert.affected_entities.slice(0,2).map((ent) => (
                        <span key={ent} className="bg-slate-200 text-slate-700 text-[10px] px-2 py-0.5 rounded border border-slate-300">{ent}</span>
                      ))}
                      {alert.affected_entities.length > 2 && <span className="text-[10px] text-slate-500">+{alert.affected_entities.length - 2}</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button 
                      onClick={() => setSelectedAlert(alert)}
                      className="text-white bg-[#0056B3] hover:bg-[#004494] focus:ring-2 focus:ring-[#0056B3]/50 focus:outline-none focus:ring-offset-1 font-medium rounded text-xs px-3 py-1.5 transition-colors"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
              {alerts.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500 italic">No active alerts found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm transition-opacity">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
             <div className="bg-[#152A38] px-6 py-4 flex items-center justify-between text-white">
                <h3 className="font-bold text-lg">Alert Details: {selectedAlert.id}</h3>
                <button onClick={() => setSelectedAlert(null)} className="text-slate-300 hover:text-white transition-colors">&times;</button>
             </div>
             <div className="p-6 space-y-6">
                <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 pb-4">
                  <span className={`px-3 py-1 text-xs font-bold rounded uppercase tracking-wide border ${severityColor(selectedAlert.severity)}`}>
                    Severity {(selectedAlert.severity * 100).toFixed(0)}%
                  </span>
                  <span className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-bold rounded uppercase border border-slate-200">{selectedAlert.domain}</span>
                  <ProvenanceTag url={selectedAlert.source_url} />
                </div>
                <div>
                   <h4 className="text-xl font-bold text-[#212529] mb-2">{selectedAlert.title}</h4>
                   <p className="text-slate-700 leading-relaxed text-sm bg-slate-50 p-4 rounded border border-slate-200">{selectedAlert.summary}</p>
                </div>
                <div>
                   <span className="text-xs font-bold tracking-wider text-slate-500 uppercase mb-2 block">Affected Entities</span>
                   <div className="flex flex-wrap gap-2">
                     {selectedAlert.affected_entities.map((entity) => (
                       <span key={entity} className="bg-white text-slate-700 text-sm px-3 py-1 rounded-md border border-slate-300 shadow-sm">{entity}</span>
                     ))}
                   </div>
                </div>
             </div>
             <div className="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t border-slate-200">
                <button onClick={() => setSelectedAlert(null)} className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50">Close</button>
                <button onClick={() => setSelectedAlert(null)} className="px-4 py-2 text-sm font-medium text-white bg-[#0056B3] rounded hover:bg-[#004494]">Acknowledge & Resolve</button>
             </div>
          </div>
        </div>
      )}
    </>
  );
}
