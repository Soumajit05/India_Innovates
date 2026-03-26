from __future__ import annotations

import logging
from collections import deque

from app.graph.ontology import EDGE_POLARITY
from app.models.responses import ScenarioImpact, ScenarioResponse


logger = logging.getLogger(__name__)


class ScenarioSimulator:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client

    @staticmethod
    def _time_horizon(total_days: int) -> str:
        if total_days < 7:
            return "Immediate (<1 week)"
        if total_days < 30:
            return "Short term (1-4 weeks)"
        if total_days < 180:
            return "Medium term (1-6 months)"
        return "Long term (>6 months)"

    def simulate(self, trigger_node_name: str, change_percent: float, depth: int = 3) -> ScenarioResponse:
        trigger = self.graph_client.get_node(trigger_node_name) or self.graph_client.get_node_by_name(trigger_node_name)
        if not trigger:
            raise ValueError(f"Unknown trigger node: {trigger_node_name}")

        base_magnitude = min(10.0, max(0.0, abs(change_percent) / 10.0))
        starting_sign = 1 if change_percent >= 0 else -1
        queue: deque[tuple[str, int, float, int, list[str], set[str], int, bool]] = deque(
            [(trigger.id, starting_sign, 1.0, 0, [trigger.name], {trigger.id}, 0, False)]
        )
        aggregated: dict[str, dict[str, object]] = {}
        simulation_warnings: list[str] = []

        while queue:
            node_id, direction_sign, confidence, level, path, path_nodes, elapsed_days, stale_used = queue.popleft()
            if level >= depth:
                continue

            for edge in self.graph_client.outgoing_edges(node_id):
                next_node = self.graph_client.get_node(edge.target)
                if not next_node:
                    continue
                if edge.target in path_nodes:
                    warning = f"Feedback loop detected at {next_node.name}"
                    if warning not in simulation_warnings:
                        simulation_warnings.append(warning)
                    logger.warning(warning)
                    continue

                edge_polarity = EDGE_POLARITY.get(edge.type, 0.0)
                edge_direction = -1 if edge.properties.get("direction") == "decrease" else 1
                next_sign = direction_sign * (-1 if edge_polarity < 0 else 1) * edge_direction
                next_confidence = round(confidence * edge.current_strength, 3)
                magnitude = max(0.0, min(10.0, base_magnitude * next_confidence))
                lag_days = int(edge.properties.get("lag_days", edge.properties.get("time_to_impact_days", 7)))
                total_days = elapsed_days + lag_days
                stale_edge_used = stale_used or edge.is_stale
                if edge.is_stale:
                    warning = f"Stale edge used for {next_node.name}"
                    if warning not in simulation_warnings:
                        simulation_warnings.append(warning)
                    logger.warning(warning)

                record = aggregated.get(next_node.id)
                readable_direction = "INCREASES" if next_sign >= 0 else "DECREASES"
                new_path = [*path, edge.type.value, next_node.name]
                if record is None:
                    aggregated[next_node.id] = {
                        "node": next_node,
                        "direction": readable_direction,
                        "direction_sign": next_sign,
                        "magnitude": magnitude,
                        "confidence": next_confidence,
                        "time_horizon": self._time_horizon(total_days),
                        "assumption": f"Assumes the {edge.type.value} relationship remains active without policy intervention.",
                        "path": new_path,
                        "stale_edge_used": stale_edge_used,
                    }
                else:
                    existing_sign = int(record["direction_sign"])
                    if existing_sign != next_sign:
                        record["direction"] = "CONTESTED"
                        record["magnitude"] = max(0.0, min(10.0, (float(record["magnitude"]) + magnitude) / 2))
                        record["confidence"] = round(max(float(record["confidence"]), next_confidence), 3)
                        record["time_horizon"] = self._time_horizon(total_days)
                        record["path"] = new_path
                        record["stale_edge_used"] = bool(record["stale_edge_used"]) or stale_edge_used
                        warning = f"Contested impact detected for {next_node.name}"
                        if warning not in simulation_warnings:
                            simulation_warnings.append(warning)
                    elif magnitude > float(record["magnitude"]):
                        record["magnitude"] = magnitude
                        record["confidence"] = round(max(float(record["confidence"]), next_confidence), 3)
                        record["time_horizon"] = self._time_horizon(total_days)
                        record["path"] = new_path
                        record["stale_edge_used"] = bool(record["stale_edge_used"]) or stale_edge_used

                queue.append(
                    (
                        next_node.id,
                        next_sign,
                        next_confidence,
                        level + 1,
                        new_path,
                        {*path_nodes, next_node.id},
                        total_days,
                        stale_edge_used,
                    )
                )

        impacts = [
            ScenarioImpact(
                node=record["node"],
                direction=str(record["direction"]),
                magnitude=int(round(max(0.0, min(10.0, float(record["magnitude"]))))),
                confidence=float(record["confidence"]),
                time_horizon=str(record["time_horizon"]),
                assumption=str(record["assumption"]),
                path=list(record["path"]),
                stale_edge_used=bool(record["stale_edge_used"]),
            )
            for record in aggregated.values()
        ]
        impacts.sort(key=lambda item: (item.magnitude * item.confidence, item.confidence), reverse=True)
        impacts = impacts[:8]

        if impacts:
            narrative = (
                f"A {change_percent:+.0f}% shock to {trigger.name} propagates most strongly into "
                f"{', '.join(impact.node.name for impact in impacts[:3])} across {depth} hops."
            )
        else:
            narrative = f"No downstream impacts were found for {trigger.name} within {depth} hops."

        return ScenarioResponse(
            trigger_node=trigger.name,
            change_percent=change_percent,
            impacts=impacts,
            narrative_summary=narrative,
            simulation_warnings=simulation_warnings,
        )
