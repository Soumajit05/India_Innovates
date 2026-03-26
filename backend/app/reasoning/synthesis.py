from __future__ import annotations

import json
import logging
import os
import re
import time
from statistics import mean
from typing import Any

import httpx

try:
    import anthropic
except Exception:  # pragma: no cover - import depends on installed package
    anthropic = None

from app.models.entities import GraphEdge, GraphNode, GraphPayload
from app.models.responses import Citation, StrategicBrief
from app.reasoning.causal_chain import CausalChainResult


logger = logging.getLogger(__name__)


MODEL_NAME = "claude-sonnet-4-20250514"
GEMINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_GENERATE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent"

ARGOS_SYSTEM_PROMPT = """
You are ARGOS - Adaptive Reasoning & Global Ontology System. You are a
strategic intelligence analyst. You ONLY make claims supported by the
provided knowledge graph context. NEVER introduce outside knowledge.

For EVERY factual claim, cite the graph edge like:
[NodeA] --RELATIONSHIP(conf=X.XX)--> [NodeB]

If contradicting edges exist, present BOTH sides explicitly.
Express uncertainty proportional to confidence:
  conf > 0.8 = "strongly suggests"
  0.5-0.8 = "indicates"
  0.3-0.5 = "weakly suggests"
  < 0.3 = "uncertain signal"

Structure EVERY response exactly as:
STRATEGIC ASSESSMENT: [one sentence]
KEY FINDINGS: [bullet list with citations]
RISK FACTORS: [what could make this wrong]
INDIA IMPLICATIONS: [specific India impact]
EVIDENCE: [all cited graph edges with source URLs]
OVERALL CONFIDENCE: [X/10 with justification]
""".strip()


SECTION_HEADERS = [
    "STRATEGIC ASSESSMENT",
    "KEY FINDINGS",
    "RISK FACTORS",
    "INDIA IMPLICATIONS",
    "EVIDENCE",
    "OVERALL CONFIDENCE",
]


def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or anthropic is None:
        return None
    return anthropic.AsyncAnthropic(api_key=api_key)


def get_gemini_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")


def confidence_language(score: float) -> str:
    if score > 0.8:
        return "strongly suggests"
    if score > 0.5:
        return "indicates"
    if score > 0.3:
        return "weakly suggests"
    return "is an uncertain signal for"


def render_edge(edge: GraphEdge, node_lookup: dict[str, GraphNode]) -> str:
    source = node_lookup[edge.source].name if edge.source in node_lookup else edge.source
    target = node_lookup[edge.target].name if edge.target in node_lookup else edge.target
    return f"[{source}] --{edge.type.value}(conf={edge.current_strength:.2f})--> [{target}]"


def build_citations(edges: list[GraphEdge], node_lookup: dict[str, GraphNode], limit: int = 8) -> list[Citation]:
    citations: list[Citation] = []
    for edge in edges[:limit]:
        citations.append(
            Citation(
                edge_id=edge.id,
                label=render_edge(edge, node_lookup),
                source_url=edge.source_url,
                confidence=edge.confidence,
                strength=edge.current_strength,
            )
        )
    return citations


def build_brief(
    query: str,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    chain: CausalChainResult | None = None,
    contradictions: list[str] | None = None,
) -> StrategicBrief:
    node_lookup = {node.id: node for node in nodes}
    ranked_edges = sorted(edges, key=lambda edge: edge.current_strength, reverse=True)
    top_edges = ranked_edges[:5]
    confidence_scores = [edge.current_strength for edge in top_edges] or [0.35]
    if chain:
        confidence_scores.append(chain.chain_confidence)
    overall_confidence = round(mean(confidence_scores), 3)

    lead_source = node_lookup[top_edges[0].source].name if top_edges and top_edges[0].source in node_lookup else "cross-domain dynamics"
    summary = (
        f"ARGOS {confidence_language(overall_confidence)} the dominant pattern in '{query}' is driven by {lead_source}."
    )
    key_findings = [
        f"{render_edge(edge, node_lookup)} {confidence_language(edge.current_strength)} strategic transmission."
        for edge in top_edges[:4]
    ]
    risk_factors = contradictions[:] if contradictions else []
    if not risk_factors:
        risk_factors = [
            "Lower-strength links were filtered out, so second-order effects may be understated.",
            "Live indicators may change quickly; stale edges can reduce confidence in the current picture.",
        ]
    india_implications = [finding for finding in key_findings if "India" in finding or "Indian" in finding]
    if not india_implications:
        india_implications = ["India remains exposed through dependencies or risk nodes inside the retrieved subgraph."]
    return StrategicBrief(
        strategic_assessment=summary,
        key_findings=key_findings,
        risk_factors=risk_factors,
        india_implications=india_implications,
        overall_confidence=overall_confidence,
    )


def build_synthesis(
    brief: StrategicBrief,
    citations: list[Citation],
    chain: CausalChainResult | None = None,
) -> str:
    lines = [
        f"STRATEGIC ASSESSMENT: {brief.strategic_assessment}",
        "KEY FINDINGS:",
    ]
    lines.extend(f"- {finding}" for finding in brief.key_findings)
    lines.append("RISK FACTORS:")
    lines.extend(f"- {risk}" for risk in brief.risk_factors)
    lines.append("INDIA IMPLICATIONS:")
    lines.extend(f"- {impact}" for impact in brief.india_implications)
    if chain:
        lines.append(
            f"- Chain: {' -> '.join(chain.path)} | confidence={chain.chain_confidence:.3f} | lag_days={chain.time_to_impact_days}"
        )
    lines.append("EVIDENCE:")
    lines.extend(f"- {citation.label} | {citation.source_url}" for citation in citations)
    lines.append(f"OVERALL CONFIDENCE: {round(brief.overall_confidence * 10, 1)}/10 based on retrieved edge strengths.")
    return "\n".join(lines)


def serialize_subgraph(subgraph: GraphPayload) -> str:
    payload: dict[str, Any] = {
        "nodes": [node.model_dump(mode="json") for node in subgraph.nodes],
        "edges": [
            {
                **edge.model_dump(mode="json"),
                "confidence": edge.confidence,
                "type": edge.type.value,
                "source_url": edge.source_url,
            }
            for edge in subgraph.edges
        ],
    }
    return json.dumps(payload, indent=2)


def build_llm_prompt(
    *,
    query: str,
    subgraph: GraphPayload,
    chain: CausalChainResult | None,
    contradictions: list[str],
) -> str:
    chain_payload = None
    if chain:
        chain_payload = {
            "path": chain.path,
            "chain_confidence": chain.chain_confidence,
            "time_to_impact_days": chain.time_to_impact_days,
            "warnings": chain.warnings,
        }
    return (
        f"USER QUERY:\n{query}\n\n"
        f"RETRIEVED SUBGRAPH JSON:\n{serialize_subgraph(subgraph)}\n\n"
        f"CAUSAL CHAIN:\n{json.dumps(chain_payload, indent=2) if chain_payload else 'null'}\n\n"
        f"CONTRADICTIONS:\n{json.dumps(contradictions, indent=2)}\n"
    )


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_header: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        matched = next((header for header in SECTION_HEADERS if line.startswith(f"{header}:")), None)
        if matched:
            current_header = matched
            sections.setdefault(current_header, [])
            suffix = line.split(":", 1)[1].strip()
            if suffix:
                sections[current_header].append(suffix)
            continue
        if current_header:
            sections.setdefault(current_header, []).append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _parse_bullets(block: str) -> list[str]:
    if not block:
        return []
    lines = [line.strip().lstrip("-").strip() for line in block.splitlines() if line.strip()]
    return [line for line in lines if line]


def _parse_confidence(confidence_text: str, fallback: float) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", confidence_text)
    if not match:
        return fallback
    return max(0.0, min(1.0, round(float(match.group(1)) / 10.0, 3)))


def _brief_from_text(text: str, fallback_brief: StrategicBrief) -> StrategicBrief | None:
    sections = _parse_sections(text)
    if not sections:
        return None
    return StrategicBrief(
        strategic_assessment=sections.get("STRATEGIC ASSESSMENT", fallback_brief.strategic_assessment),
        key_findings=_parse_bullets(sections.get("KEY FINDINGS", "")) or fallback_brief.key_findings,
        risk_factors=_parse_bullets(sections.get("RISK FACTORS", "")) or fallback_brief.risk_factors,
        india_implications=_parse_bullets(sections.get("INDIA IMPLICATIONS", "")) or fallback_brief.india_implications,
        overall_confidence=_parse_confidence(sections.get("OVERALL CONFIDENCE", ""), fallback_brief.overall_confidence),
    )


async def _generate_with_claude(prompt: str, query: str) -> str:
    client = get_anthropic_client()
    if client is None:
        raise RuntimeError("Anthropic client unavailable")
    start = time.perf_counter()
    response = await client.messages.create(
        model=MODEL_NAME,
        max_tokens=1500,
        system=ARGOS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    duration_ms = round((time.perf_counter() - start) * 1000)
    logger.info("LLM call completed with Claude for query '%s' in %sms", query[:80], duration_ms)
    return "".join(getattr(block, "text", "") for block in response.content).strip()


async def _generate_with_gemini(prompt: str, query: str) -> str:
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key unavailable")
    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": ARGOS_SYSTEM_PROMPT,
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1500,
        },
    }
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            GEMINI_GENERATE_URL,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
    duration_ms = round((time.perf_counter() - start) * 1000)
    logger.info("LLM call completed with Gemini for query '%s' in %sms", query[:80], duration_ms)
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


async def synthesize_query(
    *,
    query: str,
    subgraph: GraphPayload,
    citations: list[Citation],
    chain: CausalChainResult | None = None,
    contradictions: list[str] | None = None,
) -> tuple[str, StrategicBrief, bool, str | None]:
    contradictions = contradictions or []
    fallback_brief = build_brief(query, subgraph.nodes, subgraph.edges, chain=chain, contradictions=contradictions)
    fallback_text = build_synthesis(fallback_brief, citations, chain=chain)
    prompt = build_llm_prompt(query=query, subgraph=subgraph, chain=chain, contradictions=contradictions)

    try:
        if get_anthropic_client() is not None:
            text = await _generate_with_claude(prompt, query)
            brief = _brief_from_text(text, fallback_brief)
            if brief is not None:
                return text, brief, False, None
            return fallback_text, fallback_brief, True, "Claude response could not be parsed; template fallback used."
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("LLM call failure for Claude query '%s': %s", query[:80], exc)

    try:
        if get_gemini_api_key():
            text = await _generate_with_gemini(prompt, query)
            brief = _brief_from_text(text, fallback_brief)
            if brief is not None:
                return text, brief, False, None
            return fallback_text, fallback_brief, True, "Gemini response could not be parsed; template fallback used."
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("LLM call failure for Gemini query '%s': %s", query[:80], exc)
        return fallback_text, fallback_brief, True, f"Gemini call failed: {exc}. Template fallback used."

    return fallback_text, fallback_brief, True, "No supported LLM API key configured; template fallback used."
