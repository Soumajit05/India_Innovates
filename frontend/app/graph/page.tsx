"use client";

import { useEffect, useState } from "react";

import { EdgeDetail } from "../../components/graph/EdgeDetail";
import { GraphControls } from "../../components/graph/GraphControls";
import { NodeDetail } from "../../components/graph/NodeDetail";
import { OntologyGraph } from "../../components/graph/OntologyGraph";
import { getGraph } from "../../lib/api";
import type { Domain, GraphEdge, GraphNode, GraphPayload } from "../../lib/types";

const allDomains: Domain[] = ["Geopolitics", "Economics", "Defense", "Technology", "Climate", "Society"];

import { GeoNetworkMap } from "../../components/graph/GeoNetworkMap";

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
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start min-h-[calc(100vh-140px)]">
      {/* Central Content Area */}
      <div className="lg:col-span-9 flex flex-col gap-6">
        {/* Large Central White Card for Canvas */}
        <div className="bg-white shadow-md rounded-lg border border-slate-200 flex flex-col overflow-hidden relative" style={{ height: '600px' }}>
          <div className="bg-[#152A38] text-white px-4 py-3 flex justify-between items-center z-10">
            <h2 className="font-semibold text-sm tracking-wide">Ontology Graph Explorer</h2>
            <span className="bg-[#0056B3] text-xs px-2 py-1 rounded font-bold">Interactive</span>
          </div>
          <div className="flex-1 relative">
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
          </div>
        </div>

        {/* GeoNetwork Map Area */}
        <GeoNetworkMap />
      </div>

      {/* Right Column Details & Controls */}
      <div className="lg:col-span-3 space-y-4 h-full overflow-y-auto pr-2 pb-10">
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 p-4">
          <GraphControls
            search={search}
            onSearchChange={setSearch}
            minConfidence={minConfidence}
            onMinConfidenceChange={setMinConfidence}
            selectedDomains={selectedDomains}
            onDomainToggle={toggleDomain}
          />
        </div>
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 p-4">
          <NodeDetail node={selectedNode} />
        </div>
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 p-4">
          <EdgeDetail edge={selectedEdge} />
        </div>
      </div>
    </div>
  );
}
