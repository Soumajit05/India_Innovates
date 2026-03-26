"use client";

import type { KeyboardEvent } from "react";

const examples = [
  "What are India's top 5 strategic vulnerabilities right now?",
  "If the US Fed raises rates by 50bp, trace the impact on Indian farmers",
  "China blockades Taiwan. What is the 90-day impact on India's IT sector?",
];

interface QueryBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value?: string) => void;
  loading: boolean;
}

export function QueryBar({ value, onChange, onSubmit, loading }: QueryBarProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="panel p-5">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end">
        <div className="flex-1">
          <p className="panel-title">Ask ARGOS</p>
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            className="mt-3 w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-4 text-base leading-7 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
            placeholder="Send a message to ARGOS. Press Enter to send, or Shift+Enter for a new line."
          />
          <p className="mt-2 text-xs text-slate-400">Press Enter to send. Use Shift+Enter for a new line.</p>
        </div>

        <button
          type="button"
          onClick={() => onSubmit()}
          disabled={loading || !value.trim()}
          className="rounded-[22px] bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-4 font-display text-sm uppercase tracking-[0.24em] text-slate-950 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onSubmit(example)}
            className="rounded-full border border-white/10 px-3 py-2 text-left text-xs text-slate-300 transition hover:border-cyan-400/30 hover:text-white"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
