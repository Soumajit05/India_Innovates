export type Domain =
  | "Geopolitics"
  | "Economics"
  | "Defense"
  | "Technology"
  | "Climate"
  | "Society";

export interface GraphNode {
  id: string;
  label: string;
  name: string;
  domain: Domain;
  connections: number;
  properties: Record<string, unknown>;
  last_updated: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  confidence: number;
  strength?: number;
  current_strength: number;
  source_url: string;
  source_credibility: number;
  created_at: string;
  updated_at: string;
  decay_rate: number;
  tags: string[];
  properties: Record<string, unknown>;
  is_stale?: boolean;
}

export interface GraphPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Citation {
  edge_id: string;
  label: string;
  source_url: string;
  confidence: number;
  strength: number;
}

export interface StrategicBrief {
  strategic_assessment: string;
  key_findings: string[];
  risk_factors: string[];
  india_implications: string[];
  overall_confidence: number;
}

export interface QueryResponse {
  query_id: string;
  synthesis: string;
  brief: StrategicBrief;
  citations: Citation[];
  subgraph: GraphPayload;
  contradictions: string[];
  grounding_rate: number;
  grounding_details?: Record<string, unknown>;
  llm_fallback_used?: boolean;
  warning?: string | null;
  query_time_ms: number;
  causal_chain?: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    chain_confidence: number;
    path: string[];
    explanation: string;
    time_to_impact_days: number;
    warnings?: string[];
  } | null;
}

export interface AlertItem {
  id: string;
  title: string;
  summary: string;
  domain: Domain;
  severity: number;
  source_url: string;
  created_at: string;
  affected_entities: string[];
}

export interface DashboardMetric {
  label: string;
  value: string;
  delta: string;
}

export interface DomainMatrixCell {
  from_domain: Domain;
  to_domain: Domain;
  value: number;
}

export interface IndiaRiskState {
  state: string;
  score: number;
  driver: string;
}

export interface DashboardOverview {
  metrics: DashboardMetric[];
  domain_matrix: DomainMatrixCell[];
  alerts: AlertItem[];
  india_risk_overlay: IndiaRiskState[];
  top_vulnerabilities: Citation[];
  risk_breakdown?: Record<string, number>;
}

export interface ScenarioImpact {
  node: GraphNode;
  direction: string;
  magnitude: number;
  confidence: number;
  time_horizon: string;
  assumption: string;
  path: string[];
  stale_edge_used?: boolean;
}

export interface ScenarioResponse {
  trigger_node: string;
  change_percent: number;
  impacts: ScenarioImpact[];
  narrative_summary: string;
  simulation_warnings?: string[];
}

export interface ScenarioTemplate {
  trigger_node: string;
  change_percent: number;
  label: string;
}
