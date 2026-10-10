from __future__ import annotations

from functools import lru_cache
from typing import Iterable


def exact_load_bottom_up(weights: Iterable[int], target: int) -> list[int]:
    """Find one subset that exactly fills a target load using bottom-up DP.

    Time: O(n * target), Space: O(n * target).
    """
    items = list(weights)
    if target < 0 or any(weight < 0 for weight in items):
        raise ValueError("Weights and target must be non-negative")

    n = len(items)
    possible = [[False] * (target + 1) for _ in range(n + 1)]
    possible[0][0] = True

    for i, weight in enumerate(items, start=1):
        for total in range(target + 1):
            possible[i][total] = possible[i - 1][total]
            if total >= weight:
                possible[i][total] = possible[i][total] or possible[i - 1][total - weight]

    if not possible[n][target]:
        return []

    selected: list[int] = []
    total = target
    for i in range(n, 0, -1):
        weight = items[i - 1]
        if possible[i - 1][total]:
            continue
        selected.append(weight)
        total -= weight
    selected.reverse()
    return selected


def exact_load_top_down(weights: Iterable[int], target: int) -> list[int]:
    """Memoised variant of exact load selection."""
    items = tuple(weights)
    if target < 0 or any(weight < 0 for weight in items):
        raise ValueError("Weights and target must be non-negative")

    @lru_cache(maxsize=None)
    def solve(index: int, remaining: int):
        if remaining == 0:
            return ()
        if index == len(items) or remaining < 0:
            return None

        without = solve(index + 1, remaining)
        if without is not None:
            return without

        with_current = solve(index + 1, remaining - items[index])
        if with_current is not None:
            return (items[index],) + with_current
        return None

    result = solve(0, target)
    return list(result) if result is not None else []


def exact_load_bruteforce(weights: Iterable[int], target: int) -> list[int]:
    """Reference exponential solver used only for benchmarking small inputs."""
    items = list(weights)

    def search(index: int, remaining: int) -> list[int] | None:
        if remaining == 0:
            return []
        if index == len(items) or remaining < 0:
            return None
        chosen = search(index + 1, remaining - items[index])
        if chosen is not None:
            return [items[index], *chosen]
        return search(index + 1, remaining)

    result = search(0, target)
    return result or []
