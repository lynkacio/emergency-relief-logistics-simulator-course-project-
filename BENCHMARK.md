# Benchmark Notes

This repository includes a small benchmark comparing the reference brute-force subset search with the bottom-up dynamic-programming vehicle-loading solver.

Example run from the development environment:

| Number of items | Brute force (ms) | DP (ms) | Approx. speed-up |
|---:|---:|---:|---:|
| 10 | 0.1191 | 0.0833 | 1.4x |
| 14 | 1.5496 | 0.1451 | 10.7x |
| 18 | 28.9002 | 0.3136 | 92.2x |
| 22 | 392.2939 | 0.5379 | 729.3x |

These timings are machine-dependent and should not be treated as universal performance claims. Re-run `python scripts/benchmark.py` on your own machine before quoting benchmark values externally.

The key algorithmic distinction is stable: exhaustive subset search has `O(2^n)` worst-case growth, while the DP formulation runs in pseudo-polynomial `O(nW)` time, where `W` is the target load.
