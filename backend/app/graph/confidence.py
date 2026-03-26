from __future__ import annotations

from functools import reduce
from operator import mul


def propagate_confidence(chain: list[float]) -> float:
    if not chain:
        return 0.0
    return round(reduce(mul, chain, 1.0), 3)
