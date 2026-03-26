from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.entities import Domain, GraphEdge, GraphNode, GraphPayload


class Citation(BaseModel):
    edge_id: str
    label: str
    source_url: str
    confidence: float
    strength: float


class StrategicBrief(BaseModel):
    strategic_assessment: str
    key_findings: list[str]
    risk_factors: list[str]
    india_implications: list[str]
    overall_confidence: float = Field(ge=0.0, le=1.0)


class CausalChainResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    chain_confidence: float
    path: list[str]
    explanation: str
    time_to_impact_days: int
    warnings: list[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    query: str
    max_hops: int = Field(default=3, ge=1, le=5)
    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    query_id: str
    synthesis: str
    brief: StrategicBrief
    citations: list[Citation]
    subgraph: GraphPayload
    causal_chain: CausalChainResponse | None = None
    contradictions: list[str] = Field(default_factory=list)
    grounding_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    grounding_details: dict[str, Any] = Field(default_factory=dict)
    llm_fallback_used: bool = False
    warning: str | None = None
    query_time_ms: int


class AlertItem(BaseModel):
    id: str
    title: str
    summary: str
    domain: Domain
    severity: float = Field(ge=0.0, le=1.0)
    source_url: str
    created_at: datetime
    affected_entities: list[str]


class DashboardMetric(BaseModel):
    label: str
    value: str
    delta: str


class DomainMatrixCell(BaseModel):
    from_domain: Domain
    to_domain: Domain
    value: int


class IndiaRiskState(BaseModel):
    state: str
    score: float = Field(ge=0.0, le=100.0)
    driver: str


class DashboardOverview(BaseModel):
    metrics: list[DashboardMetric]
    domain_matrix: list[DomainMatrixCell]
    alerts: list[AlertItem]
    india_risk_overlay: list[IndiaRiskState]
    top_vulnerabilities: list[Citation]
    risk_breakdown: dict[str, float] = Field(default_factory=dict)


class GraphExplorerResponse(BaseModel):
    graph: GraphPayload


class ScenarioRequest(BaseModel):
    trigger_node: str
    change_percent: float
    depth: int = Field(default=3, ge=1, le=5)


class ScenarioImpact(BaseModel):
    node: GraphNode
    direction: str
    magnitude: int = Field(ge=0, le=10)
    confidence: float = Field(ge=0.0, le=1.0)
    time_horizon: str
    assumption: str
    path: list[str]
    stale_edge_used: bool = False


class ScenarioResponse(BaseModel):
    trigger_node: str
    change_percent: float
    impacts: list[ScenarioImpact]
    narrative_summary: str
    simulation_warnings: list[str] = Field(default_factory=list)


class DemoIngestionResponse(BaseModel):
    ingested_documents: int
    created_nodes: int
    created_edges: int
    graph: GraphPayload


class FeedbackRequest(BaseModel):
    query_id: str
    rating: int = Field(ge=1, le=5)
    cited_node_ids: list[str] = Field(default_factory=list)
    flagged_edge_ids: list[str] = Field(default_factory=list)
    comment: str | None = None


class FeedbackStatsResponse(BaseModel):
    total_queries_rated: int
    average_rating: float
    total_edges_flagged: int
    total_nodes_cited: int
