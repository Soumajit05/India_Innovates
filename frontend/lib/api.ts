import type {
  AlertItem,
  DashboardOverview,
  GraphPayload,
  QueryResponse,
  ScenarioResponse,
  ScenarioTemplate,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011/api";
const API_KEY = process.env.NEXT_PUBLIC_ARGOS_API_KEY ?? "argos-demo-key";

const fallbackGraph: GraphPayload = {
  nodes: [
    {
      id: "india",
      label: "Country",
      name: "India",
      domain: "Geopolitics",
      connections: 5,
      properties: { aliases: ["Indian state"] },
      last_updated: "2026-03-26T12:00:00Z",
    },
    {
      id: "chip",
      label: "Risk",
      name: "India Semiconductor Import Dependency",
      domain: "Technology",
      connections: 3,
      properties: {},
      last_updated: "2026-03-26T12:00:00Z",
    },
    {
      id: "water",
      label: "Risk",
      name: "India Water Treaty Exposure",
      domain: "Climate",
      connections: 3,
      properties: {},
      last_updated: "2026-03-26T12:00:00Z",
    },
  ],
  edges: [
    {
      id: "e1",
      source: "india",
      target: "chip",
      type: "DEPENDS_ON",
      confidence: 0.89,
      strength: 0.89,
      current_strength: 0.89,
      source_url: "https://www.nasscom.in",
      source_credibility: 0.8,
      created_at: "2026-03-25T12:00:00Z",
      updated_at: "2026-03-26T12:00:00Z",
      decay_rate: 0.08,
      tags: ["technology"],
      properties: {},
    },
    {
      id: "e2",
      source: "india",
      target: "water",
      type: "THREATENS",
      confidence: 0.81,
      strength: 0.81,
      current_strength: 0.81,
      source_url: "https://www.imd.gov.in",
      source_credibility: 0.94,
      created_at: "2026-03-25T12:00:00Z",
      updated_at: "2026-03-26T12:00:00Z",
      decay_rate: 0.12,
      tags: ["climate"],
      properties: {},
    },
  ],
};

const fallbackDashboard: DashboardOverview = {
  metrics: [
    { label: "Total Nodes", value: "38", delta: "+12 this week" },
    { label: "Edges In Last 24h", value: "27", delta: "+7 live" },
    { label: "Active Alerts", value: "8", delta: "3 high severity" },
    { label: "India Risk Score", value: "81", delta: "Elevated" },
  ],
  domain_matrix: [
    { from_domain: "Geopolitics", to_domain: "Economics", value: 7 },
    { from_domain: "Geopolitics", to_domain: "Technology", value: 5 },
    { from_domain: "Climate", to_domain: "Society", value: 4 },
    { from_domain: "Economics", to_domain: "Society", value: 6 },
    { from_domain: "Technology", to_domain: "Economics", value: 5 },
    { from_domain: "Defense", to_domain: "Geopolitics", value: 3 },
  ],
  alerts: [
    {
      id: "a1",
      title: "Taiwan Strait Conflict DEGRADES TSMC Production",
      summary: "Confidence 0.88 and short time-to-impact on downstream India tech supply chains.",
      domain: "Technology",
      severity: 0.93,
      source_url: "https://www.reuters.com",
      created_at: "2026-03-26T11:45:00Z",
      affected_entities: ["Taiwan Strait Conflict", "TSMC Production"],
    },
    {
      id: "a2",
      title: "IMD Monsoon Forecast CAUSES Kharif Output",
      summary: "Patchy rainfall keeps food inflation and rural stress elevated in central India.",
      domain: "Climate",
      severity: 0.86,
      source_url: "https://www.imd.gov.in",
      created_at: "2026-03-26T11:30:00Z",
      affected_entities: ["IMD Monsoon Forecast", "Kharif Output"],
    },
  ],
  india_risk_overlay: [
    { state: "Uttar Pradesh", score: 81, driver: "Food CPI + election risk" },
    { state: "Maharashtra", score: 78, driver: "Monsoon stress + rural pressure" },
    { state: "Bihar", score: 77, driver: "Rural distress" },
    { state: "Madhya Pradesh", score: 74, driver: "Monsoon sensitivity" },
    { state: "Rajasthan", score: 69, driver: "Rainfall volatility" },
  ],
  top_vulnerabilities: [
    { edge_id: "e1", label: "India -> DEPENDS_ON -> India Oil Import Dependency", source_url: "https://www.worldbank.org", confidence: 0.92, strength: 0.92 },
    { edge_id: "e2", label: "India -> DEPENDS_ON -> India Semiconductor Import Dependency", source_url: "https://www.nasscom.in", confidence: 0.89, strength: 0.89 },
    { edge_id: "e3", label: "India -> THREATENS -> India Water Treaty Exposure", source_url: "https://www.imd.gov.in", confidence: 0.81, strength: 0.81 },
  ],
};

const fallbackQuery: QueryResponse = {
  query_id: "fallback-query",
  synthesis:
    "STRATEGIC ASSESSMENT: ARGOS indicates India's technology stack remains exposed to supply-side shocks in Taiwan.\nKEY FINDINGS:\n- [India] --DEPENDS_ON(conf=0.89)--> [India Semiconductor Import Dependency]\nRISK FACTORS:\n- Live market conditions may move faster than the current graph snapshot.\nINDIA IMPLICATIONS:\n- India retains critical import exposure in semiconductors and oil.\nEVIDENCE:\n- [India] --DEPENDS_ON(conf=0.89)--> [India Semiconductor Import Dependency] | Source: https://www.nasscom.in\nOVERALL CONFIDENCE: 8.2/10",
  brief: {
    strategic_assessment: "India remains most exposed through imported semiconductors, energy, and water stress pathways.",
    key_findings: [
      "[India] --DEPENDS_ON(conf=0.89)--> [India Semiconductor Import Dependency]",
      "[India] --THREATENS(conf=0.81)--> [India Water Treaty Exposure]",
    ],
    risk_factors: ["Live data ingestion is not yet connected in fallback mode."],
    india_implications: ["India-facing supply chain fragility is already visible in the ontology graph."],
    overall_confidence: 0.82,
  },
  citations: fallbackDashboard.top_vulnerabilities,
  subgraph: fallbackGraph,
  contradictions: [],
  grounding_rate: 0.92,
  query_time_ms: 214,
  causal_chain: {
    nodes: fallbackGraph.nodes,
    edges: fallbackGraph.edges,
    chain_confidence: 0.71,
    path: ["India", "DEPENDS_ON", "India Semiconductor Import Dependency"],
    explanation: "The query resolves to a compact dependency chain centered on India-facing technology risk.",
    time_to_impact_days: 14,
  },
};

const fallbackAlerts: AlertItem[] = fallbackDashboard.alerts;

const fallbackTemplates: ScenarioTemplate[] = [
  { trigger_node: "US Fed Funds Rate", change_percent: 50, label: "US Fed Rate Hike -> India Farmer Distress" },
  { trigger_node: "Taiwan Strait Conflict", change_percent: 60, label: "Taiwan Blockade -> India Tech Sector" },
  { trigger_node: "Pakistan Stability Index", change_percent: -35, label: "Pakistan Instability -> Border Security" },
];

const fallbackScenario: ScenarioResponse = {
  trigger_node: "Taiwan Strait Conflict",
  change_percent: 60,
  impacts: [
    {
      node: {
        id: "tsmc",
        label: "Organization",
        name: "TSMC Production",
        domain: "Technology",
        connections: 4,
        properties: {},
        last_updated: "2026-03-26T12:00:00Z",
      },
      direction: "destabilizes",
      magnitude: 8,
      confidence: 0.88,
      time_horizon: "Immediate (<1 week)",
      assumption: "Assumes the disruption remains active for the first shock window.",
      path: ["Taiwan Strait Conflict", "DEGRADES", "TSMC Production"],
    },
  ],
  narrative_summary: "A Taiwan shock immediately degrades chip supply and then flows into India hardware cost pressure.",
  simulation_warnings: [],
};

async function requestJson<T>(path: string, init: RequestInit, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getDashboardOverview(): Promise<DashboardOverview> {
  return requestJson("/dashboard/overview", { method: "GET" }, fallbackDashboard);
}

export async function runQuery(query: string): Promise<QueryResponse> {
  return requestJson("/query", { method: "POST", body: JSON.stringify({ query }) }, fallbackQuery);
}

export async function getGraph(search?: string): Promise<GraphPayload> {
  const suffix = search ? `/graph/explorer?search=${encodeURIComponent(search)}` : "/graph/explorer";
  const response = await requestJson<{ graph: GraphPayload }>(suffix, { method: "GET" }, { graph: fallbackGraph });
  return response.graph;
}

export async function getAlerts(): Promise<AlertItem[]> {
  return requestJson("/alerts", { method: "GET" }, fallbackAlerts);
}

export async function getScenarioTemplates(): Promise<ScenarioTemplate[]> {
  return requestJson("/scenarios/templates", { method: "GET" }, fallbackTemplates);
}

export async function simulateScenario(trigger_node: string, change_percent: number): Promise<ScenarioResponse> {
  return requestJson(
    "/scenarios/simulate",
    { method: "POST", body: JSON.stringify({ trigger_node, change_percent }) },
    fallbackScenario,
  );
}
