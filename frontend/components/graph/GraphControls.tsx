"use client";

import type { Domain } from "@/lib/types";

const domains: Domain[] = ["Geopolitics", "Economics", "Defense", "Technology", "Climate", "Society"];

interface GraphControlsProps {
  search: string;
  onSearchChange: (value: string) => void;
  minConfidence: number;
  onMinConfidenceChange: (value: number) => void;
  selectedDomains: Domain[];
  onDomainToggle: (domain: Domain) => void;
}

export function GraphControls({
  search,
  onSearchChange,
  minConfidence,
  onMinConfidenceChange,
  selectedDomains,
  onDomainToggle,
}: GraphControlsProps) {
  return (
    <div className="panel space-y-5 p-5">
      <div>
        <p className="panel-title">Filters</p>
        <h2 className="mt-2 font-display text-2xl text-white">Graph Controls</h2>
      </div>
      <label className="block">
        <span className="eyebrow">Search nodes</span>
        <input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="India, Taiwan, monsoon, Fed..."
          className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
        />
      </label>
      <div>
        <div className="flex items-center justify-between">
          <span className="eyebrow">Confidence threshold</span>
          <span className="font-mono text-xs text-cyan-200">{minConfidence.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min={0.2}
          max={0.95}
          step={0.05}
          value={minConfidence}
          onChange={(event) => onMinConfidenceChange(Number(event.target.value))}
          className="mt-3 w-full accent-cyan-300"
        />
      </div>
      <div>
        <p className="eyebrow">Domain filters</p>
        <div className="mt-3 grid gap-2">
          {domains.map((domain) => {
            const active = selectedDomains.includes(domain);
            return (
              <button
                key={domain}
                type="button"
                onClick={() => onDomainToggle(domain)}
                className={`rounded-2xl border px-4 py-3 text-left text-sm transition ${
                  active
                    ? "border-cyan-400/35 bg-cyan-400/10 text-white"
                    : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:text-white"
                }`}
              >
                {domain}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
