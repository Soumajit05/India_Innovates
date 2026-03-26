import type { Domain, GraphEdge, GraphNode } from "@/lib/types";

const DOMAIN_COLORS: Record<Domain, string> = {
  Geopolitics: "#ff7a59",
  Economics: "#f7b84b",
  Defense: "#ff5c73",
  Technology: "#58c4ff",
  Climate: "#35d0aa",
  Society: "#d6e3f0",
};

export function domainColor(domain: Domain): string {
  return DOMAIN_COLORS[domain];
}

export function layoutNodes(nodes: GraphNode[]): Record<string, { x: number; y: number }> {
  const domains = Array.from(new Set(nodes.map((node) => node.domain)));
  const positions: Record<string, { x: number; y: number }> = {};
  domains.forEach((domain, domainIndex) => {
    const domainNodes = nodes.filter((node) => node.domain === domain);
    domainNodes.forEach((node, nodeIndex) => {
      const angle = (Math.PI * 2 * nodeIndex) / Math.max(domainNodes.length, 1);
      const ring = 110 + domainIndex * 55;
      positions[node.id] = {
        x: 320 + Math.cos(angle) * ring,
        y: 240 + Math.sin(angle) * ring,
      };
    });
  });
  return positions;
}

export function linkWidth(edge: GraphEdge): number {
  return Math.max(1.5, edge.current_strength * 5);
}

export function nodeRadius(node: GraphNode): number {
  return Math.max(10, Math.min(24, 8 + node.connections * 1.1));
}
