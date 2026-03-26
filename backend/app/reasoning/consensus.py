"""
Multi-source truth reconciliation and consensus scoring.
Detects conflicting information and assigns confidence via weighted voting.
"""
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class MultiSourceConsensus:
    """
    Reconciles conflicting information from multiple sources.
    Uses credibility-weighted voting to determine likely true statement.
    """
    
    # Source credibility scores (0-1)
    SOURCE_CREDIBILITY = {
        "WORLDBANK": 0.95,
        "IMF": 0.93,
        "REUTERS": 0.85,
        "BBC": 0.85,
        "HINDU": 0.80,
        "NDTV": 0.80,
        "GDELT": 0.75,
        "RSS": 0.70,
        "TWITTER": 0.45,
        "UNVERIFIED": 0.30,
    }
    
    def __init__(self):
        """Initialize consensus engine."""
        self.claims_history = []  # Track all claims for provenance
    
    def register_claim(
        self,
        claim_id: str,
        source: str,
        claim_type: str,  # "entity_property", "relationship", "metric"
        subject: str,  # What the claim is about
        predicate: str,  # What property/relation
        value: str,  # The claimed value
        timestamp: datetime = None,
        additional_metadata: Dict = None
    ) -> Dict:
        """
        Register a claim from a source.
        
        Args:
            claim_id: Unique claim identifier
            source: Data source name
            claim_type: Type of claim
            subject: Entity subject
            predicate: Property/relation
            value: Claimed value
            timestamp: When claim was made
            additional_metadata: Extra context
            
        Returns:
            Claim record with metadata
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        credibility = self.SOURCE_CREDIBILITY.get(source.upper(), 0.5)
        
        claim = {
            "id": claim_id,
            "source": source,
            "type": claim_type,
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "timestamp": timestamp,
            "credibility": credibility,
            "metadata": additional_metadata or {}
        }
        
        self.claims_history.append(claim)
        return claim
    
    def reconcile_claims(self, subject: str, predicate: str) -> Optional[Dict]:
        """
        Resolve conflicting claims via weighted voting.
        
        Args:
            subject: Entity subject
            predicate: Property being claimed
            
        Returns:
            Consensus result with confidence level
        """
        # Find all claims for this subject-predicate pair
        relevant_claims = [
            c for c in self.claims_history
            if c["subject"] == subject and c["predicate"] == predicate
        ]
        
        if not relevant_claims:
            return None
        
        if len(relevant_claims) == 1:
            claim = relevant_claims[0]
            return {
                "subject": subject,
                "predicate": predicate,
                "value": claim["value"],
                "confidence": claim["credibility"],
                "sources": [claim["source"]],
                "consensus_type": "single_source"
            }
        
        # Multiple claims: use weighted voting
        value_scores = defaultdict(float)
        value_sources = defaultdict(list)
        
        for claim in relevant_claims:
            value = str(claim["value"])
            credibility = claim["credibility"]
            
            value_scores[value] += credibility
            value_sources[value].append(claim["source"])
        
        # Find winning value
        winning_value = max(value_scores, key=value_scores.get)
        winning_score = value_scores[winning_value]
        total_score = sum(value_scores.values())
        
        # Calculate confidence (winning score / total score)
        confidence = winning_score / total_score if total_score > 0 else 0
        
        # Check agreement level
        n_sources = len(relevant_claims)
        n_agreeing = len(value_sources[winning_value])
        agreement_ratio = n_agreeing / n_sources
        
        consensus_type = "strong" if agreement_ratio >= 0.8 else "weak" if agreement_ratio >= 0.5 else "disputed"
        
        return {
            "subject": subject,
            "predicate": predicate,
            "value": winning_value,
            "confidence": confidence,
            "sources": value_sources[winning_value],
            "n_sources": n_sources,
            "agreement_ratio": agreement_ratio,
            "consensus_type": consensus_type,
            "alternative_values": [
                {"value": v, "score": value_scores[v], "sources": value_sources[v]} 
                for v in sorted(value_scores.keys(), key=value_scores.get, reverse=True)[1:3]
            ]
        }
    
    def detect_contradictions(self, threshold: float = 0.3) -> List[Dict]:
        """
        Detect major contradictions in claims.
        
        Args:
            threshold: Min contradiction score to flag (0-1)
            
        Returns:
            List of contradiction records
        """
        # Group by subject-predicate
        groups = defaultdict(list)
        for claim in self.claims_history:
            key = (claim["subject"], claim["predicate"])
            groups[key].append(claim)
        
        contradictions = []
        
        for (subject, predicate), claims in groups.items():
            if len(claims) < 2:
                continue
            
            # Check for value disagreement
            values = set(str(c["value"]) for c in claims)
            if len(values) < 2:
                continue
            
            # Calculate contradiction severity
            value_claims = defaultdict(list)
            for claim in claims:
                value_claims[str(claim["value"])].append(claim)
            
            # Contradiction score = product of competing credibilities
            sorted_values = sorted(value_claims.items(), 
                                  key=lambda x: sum(c["credibility"] for c in x[1]), 
                                  reverse=True)
            
            if len(sorted_values) >= 2:
                score1 = sum(c["credibility"] for c in sorted_values[0][1])
                score2 = sum(c["credibility"] for c in sorted_values[1][1])
                
                contradiction_severity = min(score1, score2) / (score1 + score2)
                
                if contradiction_severity >= threshold:
                    contradictions.append({
                        "subject": subject,
                        "predicate": predicate,
                        "severity": contradiction_severity,
                        "competing_claims": [
                            {
                                "value": value,
                                "score": sum(c["credibility"] for c in claims_list),
                                "sources": [c["source"] for c in claims_list]
                            }
                            for value, claims_list in sorted_values
                        ]
                    })
        
        return contradictions
    
    def get_provenance_trail(self, subject: str, predicate: str, value: str = None) -> List[Dict]:
        """
        Get full audit trail for a claim.
        
        Args:
            subject: Entity subject
            predicate: Property
            value: Optional specific value to filter by
            
        Returns:
            Chronological list of all claims
        """
        trail = [
            c for c in self.claims_history
            if c["subject"] == subject and c["predicate"] == predicate
        ]
        
        if value:
            trail = [c for c in trail if str(c["value"]) == str(value)]
        
        return sorted(trail, key=lambda x: x["timestamp"])
    
    def get_reliability_report(self) -> Dict:
        """Generate reliability statistics."""
        if not self.claims_history:
            return {"total_claims": 0}
        
        sources = defaultdict(int)
        types = defaultdict(int)
        
        for claim in self.claims_history:
            sources[claim["source"]] += 1
            types[claim["type"]] += 1
        
        # Identify conflicts
        contradictions = self.detect_contradictions(threshold=0.2)
        
        return {
            "total_claims": len(self.claims_history),
            "sources": dict(sources),
            "claim_types": dict(types),
            "contradictions_detected": len(contradictions),
            "contradiction_severity": sum(c["severity"] for c in contradictions) / len(contradictions) if contradictions else 0,
            "timestamp": datetime.utcnow().isoformat()
        }


class ConfidenceAggregator:
    """Aggregates confidence scores from multiple reasoning paths."""
    
    @staticmethod
    def aggregate_confidence(
        confidence_scores: List[float],
        weights: List[float] = None,
        method: str = "weighted_mean"
    ) -> float:
        """
        Aggregate multiple confidence values.
        
        Args:
            confidence_scores: List of scores (0-1)
            weights: Optional weights for each score
            method: Aggregation method
            
        Returns:
            Aggregated confidence (0-1)
        """
        if not confidence_scores:
            return 0.0
        
        if weights is None:
            weights = [1.0] * len(confidence_scores)
        
        if len(weights) != len(confidence_scores):
            weights = [1.0] * len(confidence_scores)
        
        if method == "weighted_mean":
            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0
            return sum(s * w for s, w in zip(confidence_scores, weights)) / total_weight
        
        elif method == "min":
            return min(confidence_scores)
        
        elif method == "max":
            return max(confidence_scores)
        
        elif method == "geometric_mean":
            import math
            product = 1.0
            for score in confidence_scores:
                product *= max(score, 0.01)  # Avoid 0
            return product ** (1.0 / len(confidence_scores))
        
        else:
            # Default to arithmetic mean
            return sum(confidence_scores) / len(confidence_scores)


# Global instance
consensus_engine = MultiSourceConsensus()
