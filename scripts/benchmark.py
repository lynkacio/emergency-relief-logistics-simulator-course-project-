"""Small benchmark comparing exponential subset search with dynamic programming."""

from __future__ import annotations

import random
import time

from relief_planner.allocation import exact_load_bottom_up, exact_load_bruteforce


def timed(func, items, target):
    start = time.perf_counter()
    result = func(items, target)
    return (time.perf_counter() - start) * 1000, result


def main():
    random.seed(7)
    print("items,bruteforce_ms,dp_ms")
    for n in [10, 14, 18, 22]:
        # Odd numbers + an impossible odd target force the brute-force solver to
        # explore nearly the whole search tree while DP fills a bounded table.
        items = [random.randrange(2, 40, 2) for _ in range(n)]
        target = sum(items) // 2
        if target % 2 == 0:
            target += 1
        brute_ms, _ = timed(exact_load_bruteforce, items, target)
        dp_ms, _ = timed(exact_load_bottom_up, items, target)
        print(f"{n},{brute_ms:.4f},{dp_ms:.4f}")


if __name__ == "__main__":
    main()
