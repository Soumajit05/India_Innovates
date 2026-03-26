from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Domain(StrEnum):
    GEOPOLITICS = "Geopolitics"
    ECONOMICS = "Economics"
    DEFENSE = "Defense"
    TECHNOLOGY = "Technology"
    CLIMATE = "Climate"
    SOCIETY = "Society"


class NodeLabel(StrEnum):
    COUNTRY = "Country"
    INDICATOR = "Indicator"
    EVENT = "Event"
    ORGANIZATION = "Organization"
    REGION = "Region"
    SECTOR = "Sector"
    POLICY = "Policy"
    RISK = "Risk"
    CLAIM = "Claim"


class EdgeType(StrEnum):
    CAUSES = "CAUSES"
    CORRELATES_WITH = "CORRELATES_WITH"
    THREATENS = "THREATENS"
    ENABLES = "ENABLES"
    DEGRADES = "DEGRADES"
    DEPENDS_ON = "DEPENDS_ON"
    CONTRADICTS = "CONTRADICTS"
    SIGNALS = "SIGNALS"
    STABILIZES = "STABILIZES"
    IMPACTS = "IMPACTS"


class GraphNode(BaseModel):
    id: str
    label: NodeLabel
    name: str
    domain: Domain
    connections: int = 0
    properties: dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: EdgeType
    confidence: float = Field(ge=0.0, le=1.0)
    strength: float | None = Field(default=None, ge=0.0, le=1.0)
    current_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    source_url: str
    source_credibility: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime
    updated_at: datetime
    decay_rate: float = Field(default=0.0, ge=0.0)
    tags: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
    is_stale: bool = False


class GraphPayload(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class IngestionDocument(BaseModel):
    id: str
    title: str
    body: str
    source_url: str
    source_domain: str
    published_at: datetime
    domain: Domain
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractedEntity(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float


class ExtractedRelation(BaseModel):
    head: str
    rel: EdgeType
    tail: str
    confidence: float
    properties: dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    document: IngestionDocument
    entities: list[ExtractedEntity]
    relations: list[ExtractedRelation]
    event_type: str
    geotags: list[str]
    contradictions: list[str] = Field(default_factory=list)
