# Emergency Relief Logistics Planning Simulator

A Python course project that applies classic algorithms to a concrete emergency-response scenario. The simulator models a relief coordinator who must keep a low-cost road network operational, determine how much supply can move through a constrained transport network, load vehicles efficiently, split workers into compatible teams, and correct mistyped destination names.

> This repository is an independent implementation built around standard algorithmic ideas. It is not a copy of course starter code or assessment infrastructure.

## What the project solves

After a flood or earthquake, a relief coordinator may need to answer several questions quickly:

1. **Which roads should remain in the minimum-cost backbone?**  
   Kruskal's Minimum Spanning Tree (MST) creates the initial road network. When one road cost changes, the project updates the current MST using the cycle/cut properties instead of blindly rebuilding the whole solution.

2. **How much material can reach a shelter?**  
   A residual-capacity network is searched with BFS for augmenting paths and repeatedly augmented to compute maximum transport capacity.

3. **Which packages exactly fill a vehicle?**  
   A subset-sum formulation is solved with both top-down memoisation and bottom-up dynamic programming. A brute-force reference implementation is retained only for benchmarking.

4. **Can workers be split into two conflict-free teams?**  
   Team conflicts are represented as a graph and checked for bipartiteness using BFS two-colouring.

5. **What did the operator mean when a location name was mistyped?**  
   An `O(mn)` weighted edit-distance algorithm uses QWERTY-key proximity to rank likely location names.

## Algorithms and techniques

- Python 3.10+
- Object-oriented graph data structures
- Kruskal MST + Disjoint Set Union (Union-Find)
- Incremental MST maintenance after edge-weight changes
- BFS / DFS and connected-component analysis
- Residual networks and augmenting paths
- Top-down memoisation and bottom-up dynamic programming
- Backtracking / solution reconstruction
- Bipartite graph two-colouring
- QWERTY-aware weighted edit distance
- `unittest`-based automated testing

## Repository structure

```text
emergency-relief-logistics-simulator/
├── data/
│   └── sample_scenario.json       # Example emergency scenario
├── scripts/
│   └── benchmark.py               # Brute force vs DP timing comparison
├── src/relief_planner/
│   ├── allocation.py              # Vehicle-load subset-sum solvers
│   ├── cli.py                     # Command-line entry point
│   ├── graph.py                   # Graph and flow-network data structures
│   ├── locations.py               # QWERTY-aware string matching
│   ├── network.py                 # MST updates and flow algorithms
│   ├── simulator.py               # Integrates all components
│   └── teams.py                   # Bipartite relief-team assignment
├── tests/
│   └── test_algorithms.py
├── BENCHMARK.md                  # Example timing results
├── LICENSE
├── pyproject.toml
└── README.md
```

## Run the simulator

Create a virtual environment and install the project locally:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e .
```

Run the included scenario:

```bash
relief-planner data/sample_scenario.json
```

Example output:

```text
=== Emergency Relief Logistics Report ===
Initial minimum road-network cost: ...
Updated minimum road-network cost: ...
Maximum transport capacity: ...
Selected vehicle load: ...
Relief team A: ...
Relief team B: ...
Corrected location: shelter
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Benchmark the resource-allocation algorithm

```bash
python scripts/benchmark.py
```

The brute-force subset solver has exponential worst-case growth (`O(2^n)`), while the dynamic-programming solution runs in pseudo-polynomial `O(nW)` time, where `W` is the target vehicle capacity. The benchmark script lets you replace theoretical claims with reproducible timings on your own machine.

## Example scenario format

The JSON file contains road costs, transport capacities, package weights, worker conflicts, and location names. This keeps the algorithms separate from the data and makes it easy to create additional scenarios without modifying source code.

## Why this project is structured this way

Each algorithm lives in its own module because it represents a different responsibility. `simulator.py` acts as the orchestration layer: it reads one scenario and passes each part of the data to the appropriate algorithm. This separation makes the code easier to test, explain, replace, and extend.

Possible extensions include a Tkinter or web dashboard, geographic coordinates, road closures, approximate knapsack loading, multiple shelters, and visualization of the MST and flow network.
