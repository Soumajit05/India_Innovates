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
    <div className="grid gap-6 xl:grid-cols-[0.38fr_0.62fr]">
      <div className="panel p-5">
        <div>
          <p className="panel-title">Scenario Templates</p>
          <h2 className="mt-2 font-display text-2xl text-white">Shock Propagation Simulator</h2>
        </div>
        <div className="mt-6 grid gap-3">
          {templates.map((template) => {
            const active = selectedTemplate?.label === template.label;
            return (
              <button
                key={template.label}
                type="button"
                onClick={() => setSelectedTemplate(template)}
                className={`rounded-[24px] border p-4 text-left transition ${
                  active
                    ? "border-cyan-400/40 bg-cyan-400/10"
                    : "border-white/10 bg-white/5 hover:border-white/20"
                }`}
              >
                <p className="font-display text-lg text-white">{template.label}</p>
                <p className="mt-2 font-mono text-xs uppercase tracking-[0.18em] text-slate-400">
                  {template.trigger_node} | {template.change_percent > 0 ? "+" : ""}
                  {template.change_percent}%
                </p>
              </button>
            );
          })}
        </div>
        <button
          type="button"
          onClick={() => void runSimulation()}
          className="mt-5 w-full rounded-[22px] bg-gradient-to-r from-cyan-400 to-emerald-400 px-5 py-4 font-display text-sm uppercase tracking-[0.24em] text-slate-950"
        >
          Simulate
        </button>
      </div>

      <div className="space-y-6">
        <div className="panel p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="panel-title">Impact Table</p>
              <h2 className="mt-2 font-display text-2xl text-white">Downstream Effects</h2>
            </div>
            <div className="data-pill">{result?.trigger_node ?? "Awaiting simulation"}</div>
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-300">{result?.narrative_summary ?? "Run a scenario to propagate an upstream shock through the ontology."}</p>
          <div className="mt-6 grid gap-4">
            {result?.impacts.map((impact) => (
              <div key={`${impact.node.id}-${impact.path.join("-")}`} className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-4">
                  <p className="font-display text-xl text-white">{impact.node.name}</p>
                  <p className="font-mono text-xs uppercase tracking-[0.18em] text-cyan-200">{impact.confidence * 100}% confidence</p>
                </div>
                <div className="mt-3 grid gap-3 text-sm text-slate-300 md:grid-cols-3">
                  <p>Direction: {impact.direction}</p>
                  <p>Magnitude: {impact.magnitude}/10</p>
                  <p>Time horizon: {impact.time_horizon}</p>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-400">{impact.assumption}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-5">
          <p className="panel-title">Path Narrative</p>
          <h2 className="mt-2 font-display text-2xl text-white">Hop-by-Hop Propagation</h2>
          <div className="mt-6">
            <Timeline
              items={(result?.impacts ?? []).map((impact) => ({
                title: impact.node.name,
                detail: impact.path.join(" -> "),
                meta: impact.time_horizon,
              }))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
