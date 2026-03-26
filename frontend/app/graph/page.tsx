"use client";

import { useEffect, useState } from "react";

import { EdgeDetail } from "../../components/graph/EdgeDetail";
import { GraphControls } from "../../components/graph/GraphControls";
import { NodeDetail } from "../../components/graph/NodeDetail";
import { OntologyGraph } from "../../components/graph/OntologyGraph";
import { getGraph } from "../../lib/api";
import type { Domain, GraphEdge, GraphNode, GraphPayload } from "../../lib/types";

const allDomains: Domain[] = ["Geopolitics", "Economics", "Defense", "Technology", "Climate", "Society"];

export default function GraphPage() {
  const [graph, setGraph] = useState<GraphPayload>({ nodes: [], edges: [] });
  const [search, setSearch] = useState("");
  const [selectedDomains, setSelectedDomains] = useState<Domain[]>(allDomains);
  const [minConfidence, setMinConfidence] = useState(0.25);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

  useEffect(() => {
    void getGraph(search).then((payload) => {
      setGraph(payload);
      setSelectedNode(payload.nodes[0] ?? null);
    });
  }, [search]);

  const filteredNodes = graph.nodes.filter((node) => selectedDomains.includes(node.domain));
  const allowedIds = new Set(filteredNodes.map((node) => node.id));
  const filteredEdges = graph.edges.filter(
    (edge) => edge.current_strength >= minConfidence && allowedIds.has(edge.source) && allowedIds.has(edge.target),
  );

  const toggleDomain = (domain: Domain) => {
    setSelectedDomains((current) =>
      current.includes(domain) ? current.filter((item) => item !== domain) : [...current, domain],
    );
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[0.28fr_0.72fr_0.3fr]">
      <GraphControls
        search={search}
        onSearchChange={setSearch}
        minConfidence={minConfidence}
        onMinConfidenceChange={setMinConfidence}
        selectedDomains={selectedDomains}
        onDomainToggle={toggleDomain}
      />
      <OntologyGraph
        nodes={filteredNodes}
        edges={filteredEdges}
        activeNodeId={selectedNode?.id}
        onNodeClick={(node) => {
          setSelectedNode(node);
          setSelectedEdge(null);
        }}
        onEdgeClick={(edge) => {
          setSelectedEdge(edge);
        }}
      />
      <div className="space-y-6">
        <NodeDetail node={selectedNode} />
        <EdgeDetail edge={selectedEdge} />
      </div>
    </div>
  );
}
