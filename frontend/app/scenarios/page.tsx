"use client";

import { useEffect, useState } from "react";

import { Timeline } from "../../components/shared/Timeline";
import { getScenarioTemplates, simulateScenario } from "../../lib/api";
import type { ScenarioResponse, ScenarioTemplate } from "../../lib/types";

export default function ScenariosPage() {
  const [templates, setTemplates] = useState<ScenarioTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ScenarioTemplate | null>(null);
  const [result, setResult] = useState<ScenarioResponse | null>(null);

  useEffect(() => {
    void getScenarioTemplates().then((items) => {
      setTemplates(items);
      setSelectedTemplate(items[0] ?? null);
    });
  }, []);

  const runSimulation = async () => {
    if (!selectedTemplate) {
      return;
    }
    const response = await simulateScenario(selectedTemplate.trigger_node, selectedTemplate.change_percent);
    setResult(response);
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[0.35fr_0.65fr]">
      {/* Left Column: Simulator Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 self-start sticky top-6">
        <div className="border-b border-slate-100 pb-4">
          <p className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Scenario Templates</p>
          <h2 className="mt-1 text-xl font-bold text-[#212529]">Shock Simulator</h2>
        </div>
        <div className="mt-6 flex flex-col gap-3">
          {templates.map((template) => {
            const active = selectedTemplate?.label === template.label;
            return (
              <button
                key={template.label}
                type="button"
                onClick={() => setSelectedTemplate(template)}
                className={`rounded-md border p-4 text-left transition-colors relative ${
                  active
                    ? "border-[#0056B3] bg-[#0056B3]/5 shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                }`}
              >
                {active && <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#0056B3] rounded-l-md"></div>}
                <p className={`font-bold ${active ? 'text-[#0056B3]' : 'text-[#212529]'}`}>{template.label}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                    {template.trigger_node}
                  </span>
                  <span className={`text-xs font-bold px-2 py-1 rounded border ${
                    template.change_percent > 0 
                      ? 'bg-green-100 text-green-800 border-green-300' 
                      : 'bg-red-100 text-red-800 border-red-300'
                  }`}>
                    {template.change_percent > 0 ? "+" : ""}{template.change_percent}%
                  </span>
                </div>
              </button>
            );
          })}
        </div>
        <button
          type="button"
          onClick={() => void runSimulation()}
          className="mt-6 w-full rounded-md bg-[#0056B3] hover:bg-[#004494] px-6 py-3 font-semibold text-white shadow-sm transition-colors uppercase tracking-widest text-sm"
        >
          Execute Simulation
        </button>
      </div>

      {/* Right Column: Results */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <div className="bg-[#152A38] text-white px-6 py-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-bold tracking-wide text-slate-300 uppercase">Impact Table</p>
              <h2 className="mt-1 text-lg font-bold">Downstream Effects</h2>
            </div>
            <div className="bg-[#0056B3] text-xs font-bold px-3 py-1 rounded text-white border border-[#004494]">
               Trigger: {result?.trigger_node ?? "Pending"}
            </div>
          </div>
          
          <div className="p-6">
            <p className="text-sm leading-relaxed text-slate-700 bg-[#F4F6F9] p-4 rounded-md border border-slate-200 font-medium">
              {result?.narrative_summary ?? "Select a scenario template and run the simulation to propagate an upstream shock through the standard causal ontology."}
            </p>
            
            {result && result.impacts.length > 0 && (
              <div className="mt-6 space-y-4">
                <h3 className="text-sm font-bold text-[#212529] border-b border-slate-200 pb-2">Identified Vulnerabilities</h3>
                {result.impacts.map((impact) => (
                  <div key={`${impact.node.id}-${impact.path.join("-")}`} className="rounded-md border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-3">
                      <p className="text-lg font-bold text-[#003366]">{impact.node.name}</p>
                      <span className="text-xs font-bold bg-[#FFC107]/20 text-yellow-800 border border-[#FFC107]/50 px-2 py-1 rounded">
                        {(impact.confidence * 100).toFixed(0)}% Confidence
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2 text-xs font-bold text-slate-600 mb-4 bg-slate-50 p-3 rounded border border-slate-100">
                      <div className="flex flex-col">
                        <span className="text-slate-400 uppercase tracking-wider mb-1">Direction</span>
                        <span className="text-slate-800">{impact.direction}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-slate-400 uppercase tracking-wider mb-1">Severity</span>
                        <span className="text-slate-800">{impact.magnitude}/10</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-slate-400 uppercase tracking-wider mb-1">Time Horizon</span>
                        <span className="text-slate-800">{impact.time_horizon}</span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-slate-700 leading-relaxed border-l-2 border-[#0056B3] pl-3 italic">
                      {impact.assumption}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
            <div className="border-b border-slate-100 pb-4 mb-6">
              <p className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Path Narrative</p>
              <h2 className="mt-1 text-xl font-bold text-[#212529]">Hop-by-Hop Propagation</h2>
            </div>
            <div className="pl-4 border-l-2 border-slate-200 ml-2">
              <Timeline
                items={result.impacts.map((impact) => ({
                  title: impact.node.name,
                  detail: impact.path.join(" ➔ "),
                  meta: `Horizon: ${impact.time_horizon}`,
                }))}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
