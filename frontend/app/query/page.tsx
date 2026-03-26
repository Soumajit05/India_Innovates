"use client";

import { useState } from "react";

import { NodeDetail } from "../../components/graph/NodeDetail";
import { OntologyGraph } from "../../components/graph/OntologyGraph";
import { CausalChain } from "../../components/query/CausalChain";
import { ChatTranscript, type ChatMessage } from "../../components/query/ChatTranscript";
import { CitationList } from "../../components/query/CitationList";
import { QueryBar } from "../../components/query/QueryBar";
import { ResponseCard } from "../../components/query/ResponseCard";
import { runQuery } from "../../lib/api";
import type { GraphNode, QueryResponse } from "../../lib/types";


const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Ask me anything about India's strategic vulnerabilities, causal chains, geopolitical shocks, or downstream effects. I will answer using the ARGOS graph like a chatbot and keep the supporting evidence in sync on the right.",
};


function makeMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function buildConversationPrompt(messages: ChatMessage[], prompt: string) {
  const history = messages
    .filter((message) => !message.pending)
    .slice(-6)
    .map((message) => `${message.role === "assistant" ? "ARGOS" : "User"}: ${message.content}`)
    .join("\n\n");

  if (!history) {
    return prompt;
  }

  return [
    "Continue this ARGOS conversation and answer the latest user request using the graph-grounded backend.",
    "",
    "Conversation so far:",
    history,
    "",
    `Latest user message: ${prompt}`,
  ].join("\n");
}


export default function QueryPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);

  const submit = async (overrideQuery?: string) => {
    const prompt = (overrideQuery ?? query).trim();
    if (!prompt || loading) {
      return;
    }

    const contextualPrompt = buildConversationPrompt(messages, prompt);

    const userMessage: ChatMessage = {
      id: makeMessageId(),
      role: "user",
      content: prompt,
    };
    const assistantMessageId = makeMessageId();
    const pendingAssistant: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "ARGOS is tracing the graph, ranking evidence, and drafting a grounded answer",
      pending: true,
    };

    setMessages((current) => [...current, userMessage, pendingAssistant]);
    setLoading(true);
    setQuery("");

    try {
      const response = await runQuery(contextualPrompt);
      setResult(response);
      setSelectedNode(response.subgraph.nodes[0] ?? null);
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessageId
            ? {
                ...message,
                content: response.synthesis,
                meta: `${response.query_time_ms} ms | ${Math.round(response.grounding_rate * 100)}% grounded | follow-up aware`,
                pending: false,
              }
            : message,
        ),
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Query failed.";
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantMessageId
            ? {
                ...item,
                content: `I could not complete that query: ${message}`,
                pending: false,
              }
            : item,
        ),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <div className="space-y-6">
        <ChatTranscript messages={messages} />
        <QueryBar value={query} onChange={setQuery} onSubmit={(value) => void submit(value)} loading={loading} />
        <ResponseCard result={result} />
        <CitationList citations={result?.citations ?? []} />
      </div>

      <div className="space-y-6">
        <CausalChain result={result} />
        <OntologyGraph
          nodes={result?.subgraph.nodes ?? []}
          edges={result?.subgraph.edges ?? []}
          activeNodeId={selectedNode?.id}
          onNodeClick={setSelectedNode}
        />
        <NodeDetail node={selectedNode} />
      </div>
    </div>
  );
}
