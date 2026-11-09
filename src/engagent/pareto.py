"""Pareto filtering (doc 9.3). All objectives are minimised; feasible designs only."""
from __future__ import annotations
import numpy as np


def pareto_front(points: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated rows."""
    n = len(points)
    mask = np.ones(n, bool)
    for i in range(n):
        if not mask[i]:
            continue
        dom = np.all(points <= points[i], axis=1) & np.any(points < points[i], axis=1)
        if dom.any():
            mask[i] = False
    return mask


def pareto_ranks(points: np.ndarray, max_rank: int = 5) -> np.ndarray:
    ranks = np.full(len(points), -1)
    remaining = np.arange(len(points))
    for r in range(max_rank):
        if len(remaining) == 0:
            break
        m = pareto_front(points[remaining])
        ranks[remaining[m]] = r
        remaining = remaining[~m]
    return ranks
