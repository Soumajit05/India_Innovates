from __future__ import annotations

import math
from datetime import datetime, timezone


def compute_edge_strength(confidence: float, created_at: datetime, decay_rate: float) -> float:
    if decay_rate <= 0:
        return round(confidence, 3)
    now = datetime.now(timezone.utc)
    created = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
    age_days = max((now - created).total_seconds() / 86400, 0)
    decay_factor = math.exp(-decay_rate * age_days / 365)
    return round(confidence * decay_factor, 3)
