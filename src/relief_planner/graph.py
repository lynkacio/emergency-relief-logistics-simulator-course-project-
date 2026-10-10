from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, Tuple


Edge = Tuple[str, str]


def canonical_edge(u: str, v: str) -> Edge:
    """Return a stable representation for an undirected edge."""
    return (u, v) if u <= v else (v, u)


@dataclass
class WeightedUndirectedGraph:
    """Small weighted undirected graph used by the road-planning algorithms."""

    adjacency: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def add_node(self, node: str) -> None:
        self.adjacency.setdefault(node, {})

    def add_edge(self, u: str, v: str, weight: float) -> None:
        if u == v:
            raise ValueError("Self-loops are not supported")
        if weight < 0:
            raise ValueError("Edge weights must be non-negative")
        self.add_node(u)
        self.add_node(v)
        self.adjacency[u][v] = weight
        self.adjacency[v][u] = weight

    def remove_edge(self, u: str, v: str) -> None:
        self.adjacency[u].pop(v, None)
        self.adjacency[v].pop(u, None)

    def has_edge(self, u: str, v: str) -> bool:
        return u in self.adjacency and v in self.adjacency[u]

    def weight(self, u: str, v: str) -> float:
        return self.adjacency[u][v]

    def set_weight(self, u: str, v: str, weight: float) -> None:
        if not self.has_edge(u, v):
            raise KeyError(f"Unknown edge: {u}-{v}")
        if weight < 0:
            raise ValueError("Edge weights must be non-negative")
        self.adjacency[u][v] = weight
        self.adjacency[v][u] = weight

    def neighbors(self, node: str) -> Dict[str, float]:
        return dict(self.adjacency.get(node, {}))

    @property
    def nodes(self) -> list[str]:
        return list(self.adjacency)

    def edges(self) -> Iterator[Tuple[str, str, float]]:
        seen: set[Edge] = set()
        for u, nbrs in self.adjacency.items():
            for v, w in nbrs.items():
                edge = canonical_edge(u, v)
                if edge not in seen:
                    seen.add(edge)
                    yield edge[0], edge[1], w

    def copy(self) -> "WeightedUndirectedGraph":
        clone = WeightedUndirectedGraph()
        for u, v, w in self.edges():
            clone.add_edge(u, v, w)
        for node in self.nodes:
            clone.add_node(node)
        return clone

    def total_weight(self) -> float:
        return sum(weight for _, _, weight in self.edges())


@dataclass
class DirectedFlowNetwork:
    """Directed capacity network with an explicit residual graph."""

    capacity: Dict[str, Dict[str, float]] = field(default_factory=dict)
    flow: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def add_edge(self, u: str, v: str, capacity: float) -> None:
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.capacity.setdefault(u, {})[v] = capacity
        self.capacity.setdefault(v, {})
        self.flow.setdefault(u, {})[v] = 0.0
        self.flow.setdefault(v, {}).setdefault(u, 0.0)

    @property
    def nodes(self) -> set[str]:
        return set(self.capacity)

    def residual_capacity(self, u: str, v: str) -> float:
        forward_capacity = self.capacity.get(u, {}).get(v, 0.0)
        forward_flow = self.flow.get(u, {}).get(v, 0.0)
        reverse_flow = self.flow.get(v, {}).get(u, 0.0)
        return (forward_capacity - forward_flow) + reverse_flow

    def residual_neighbors(self, u: str) -> Iterable[str]:
        candidates = set(self.capacity.get(u, {}))
        for predecessor, outgoing in self.flow.items():
            if outgoing.get(u, 0.0) > 0:
                candidates.add(predecessor)
        return (v for v in candidates if self.residual_capacity(u, v) > 0)

    def push(self, u: str, v: str, amount: float) -> None:
        if amount < 0 or amount > self.residual_capacity(u, v):
            raise ValueError("Invalid augmentation amount")

        forward_room = self.capacity.get(u, {}).get(v, 0.0) - self.flow.get(u, {}).get(v, 0.0)
        sent_forward = min(amount, max(0.0, forward_room))
        if sent_forward:
            self.flow.setdefault(u, {}).setdefault(v, 0.0)
            self.flow[u][v] += sent_forward

        remainder = amount - sent_forward
        if remainder:
            self.flow.setdefault(v, {}).setdefault(u, 0.0)
            self.flow[v][u] -= remainder
