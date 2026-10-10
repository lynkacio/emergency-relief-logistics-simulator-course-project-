from __future__ import annotations

from math import inf
from typing import Iterable


QWERTY_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
QWERTY_POS = {
    char: (row, col)
    for row, letters in enumerate(QWERTY_ROWS)
    for col, char in enumerate(letters)
}


def keyboard_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if a not in QWERTY_POS or b not in QWERTY_POS:
        return 2
    row_a, col_a = QWERTY_POS[a]
    row_b, col_b = QWERTY_POS[b]
    return abs(row_a - row_b) + abs(col_a - col_b)


def qwerty_edit_distance(source: str, target: str, gap_cost: int = 2) -> int:
    """Weighted edit distance using QWERTY key proximity for substitutions.

    Time: O(mn), Space: O(mn).
    """
    source = source.lower()
    target = target.lower()
    m, n = len(source), len(target)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        dp[i][0] = i * gap_cost
    for j in range(1, n + 1):
        dp[0][j] = j * gap_cost

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            substitution = dp[i - 1][j - 1] + keyboard_distance(source[i - 1], target[j - 1])
            deletion = dp[i - 1][j] + gap_cost
            insertion = dp[i][j - 1] + gap_cost
            dp[i][j] = min(substitution, deletion, insertion)
    return dp[m][n]


def closest_location(query: str, locations: Iterable[str]) -> tuple[str, int]:
    best_name = ""
    best_score = inf
    for location in locations:
        score = qwerty_edit_distance(query, location)
        if score < best_score:
            best_name, best_score = location, score
    if best_name == "":
        raise ValueError("At least one location is required")
    return best_name, int(best_score)
