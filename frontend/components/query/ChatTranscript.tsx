"use client";

import { useEffect, useRef } from "react";


export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: string;
  pending?: boolean;
}

export function ChatTranscript({ messages }: { messages: ChatMessage[] }) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="panel-title">ARGOS Chat</p>
          <h2 className="mt-2 font-display text-2xl text-white">Conversational Strategic Search</h2>
        </div>
        <div className="data-pill">Ontology-grounded</div>
      </div>

      <div className="mt-6 max-h-[520px] space-y-4 overflow-y-auto pr-2">
        {messages.map((message) => {
          const assistant = message.role === "assistant";
          return (
            <div
              key={message.id}
              className={`flex ${assistant ? "justify-start" : "justify-end"}`}
            >
              <div
                className={`max-w-[88%] rounded-[24px] border p-4 ${
                  assistant
                    ? "border-cyan-400/20 bg-cyan-400/8 text-slate-100"
                    : "border-emerald-400/20 bg-emerald-400/10 text-white"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-slate-300">
                    {assistant ? "ARGOS" : "You"}
                  </p>
                  {message.meta ? (
                    <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">{message.meta}</p>
                  ) : null}
                </div>
                <div className="mt-3 whitespace-pre-wrap text-sm leading-7">
                  {message.content}
                  {message.pending ? <span className="ml-1 inline-block animate-pulse">...</span> : null}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>
    </div>
  );
}
