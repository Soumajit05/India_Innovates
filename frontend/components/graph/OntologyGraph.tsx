"use client";

import { useState } from "react";

import { domainColor, layoutNodes, linkWidth, nodeRadius } from "@/lib/graph-utils";
import type { GraphEdge, GraphNode } from "@/lib/types";

interface OntologyGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  activeNodeId?: string | null;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
}

export function OntologyGraph({
  nodes,
  edges,
  activeNodeId,
  onNodeClick,
  onEdgeClick,
}: OntologyGraphProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const positions = layoutNodes(nodes);
  const nodeLookup = Object.fromEntries(nodes.map((node) => [node.id, node]));

  return (
    <div className="panel h-[520px] overflow-hidden p-3">
      <svg viewBox="0 0 640 480" className="h-full w-full rounded-[24px] bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.08),transparent_30%),linear-gradient(180deg,rgba(15,23,42,0.92),rgba(2,6,23,0.94))]">
        <defs>
          <filter id="node-glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {edges.map((edge) => {
          const source = positions[edge.source];
          const target = positions[edge.target];
          if (!source || !target) {
            return null;
          }
          return (
            <g key={edge.id} onClick={() => onEdgeClick?.(edge)} className="cursor-pointer">
              <line
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke="rgba(125, 211, 252, 0.38)"
                strokeWidth={linkWidth(edge)}
                strokeLinecap="round"
              />
              <text
                x={(source.x + target.x) / 2}
                y={(source.y + target.y) / 2 - 6}
                textAnchor="middle"
                className="fill-slate-500 font-mono text-[9px] uppercase tracking-[0.2em]"
              >
                {edge.type}
              </text>
            </g>
          );
        })}
        {nodes.map((node) => {
          const position = positions[node.id];
          if (!position) {
            return null;
          }
          const isActive = activeNodeId === node.id || hoveredNode === node.id;
          return (
            <g
              key={node.id}
              transform={`translate(${position.x}, ${position.y})`}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
              onClick={() => onNodeClick?.(node)}
              className="cursor-pointer"
            >
              <circle
                r={nodeRadius(node)}
                fill={domainColor(node.domain)}
                fillOpacity={isActive ? 0.9 : 0.75}
                stroke={isActive ? "#ffffff" : "rgba(255,255,255,0.12)"}
                strokeWidth={isActive ? 2.5 : 1}
                filter="url(#node-glow)"
              />
              <text
                y={nodeRadius(node) + 18}
                textAnchor="middle"
                className="fill-slate-200 font-display text-[11px]"
              >
                {node.name}
              </text>
            </g>
          );
        })}
        {hoveredNode && nodeLookup[hoveredNode] ? (
          <foreignObject x="18" y="18" width="220" height="110">
            <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-slate-200 backdrop-blur">
              <p className="eyebrow">{nodeLookup[hoveredNode].domain}</p>
              <p className="mt-2 font-display text-lg text-white">{nodeLookup[hoveredNode].name}</p>
              <p className="mt-2 text-xs leading-5 text-slate-300">
                {nodeLookup[hoveredNode].connections} relationships tracked in the current subgraph.
              </p>
            </div>
          </foreignObject>
        ) : null}
      </svg>
    </div>
  );
}
