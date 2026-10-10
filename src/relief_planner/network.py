from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from .graph import DirectedFlowNetwork, Edge, WeightedUndirectedGraph, canonical_edge


class DisjointSet:
    def __init__(self, nodes: Iterable[str]) -> None:
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}

    def find(self, node: str) -> str:
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def union(self, a: str, b: str) -> bool:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True


def minimum_spanning_tree(graph: WeightedUndirectedGraph) -> WeightedUndirectedGraph:
    """Compute an MST with Kruskal's algorithm."""
    tree = WeightedUndirectedGraph()
    for node in graph.nodes:
        tree.add_node(node)

    dsu = DisjointSet(graph.nodes)
    for u, v, weight in sorted(graph.edges(), key=lambda item: item[2]):
        if dsu.union(u, v):
            tree.add_edge(u, v, weight)

    if graph.nodes and sum(1 for _ in tree.edges()) != len(graph.nodes) - 1:
        raise ValueError("Road graph is disconnected; no spanning tree exists")
    return tree


def _tree_path(tree: WeightedUndirectedGraph, start: str, end: str) -> list[str]:
    queue = deque([start])
    parent: Dict[str, Optional[str]] = {start: None}
    while queue:
        node = queue.popleft()
        if node == end:
            break
        for neighbor in tree.neighbors(node):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    if end not in parent:
        return []
    path: list[str] = []
    cursor: Optional[str] = end
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    return list(reversed(path))


def _components(tree: WeightedUndirectedGraph) -> Dict[str, int]:
    component_of: Dict[str, int] = {}
    component_id = 0
    for start in tree.nodes:
        if start in component_of:
            continue
        stack = [start]
        while stack:
            node = stack.pop()
            if node in component_of:
                continue
            component_of[node] = component_id
            stack.extend(n for n in tree.neighbors(node) if n not in component_of)
        component_id += 1
    return component_of


@dataclass(frozen=True)
class MSTUpdateResult:
    removed_edge: Optional[Edge]
    added_edge: Optional[Edge]
    old_total: float
    new_total: float


def update_mst_for_weight_change(
    graph: WeightedUndirectedGraph,
    tree: WeightedUndirectedGraph,
    edge: Edge,
    new_weight: float,
) -> MSTUpdateResult:
    """Incrementally maintain an MST after one road-cost change.

    The function handles both tree and non-tree edges and only changes the
    current MST when the cut/cycle property requires it.
    """
    u, v = edge
    if not graph.has_edge(u, v):
        raise KeyError(f"Unknown road: {u}-{v}")

    old_weight = graph.weight(u, v)
    old_total = tree.total_weight()
    edge_in_tree = tree.has_edge(u, v)
    graph.set_weight(u, v, new_weight)

    if edge_in_tree and new_weight <= old_weight:
        tree.set_weight(u, v, new_weight)
        return MSTUpdateResult(None, None, old_total, tree.total_weight())

    if not edge_in_tree and new_weight >= old_weight:
        return MSTUpdateResult(None, None, old_total, tree.total_weight())

    if not edge_in_tree:
        path = _tree_path(tree, u, v)
        if not path:
            raise ValueError("Current MST is disconnected")
        max_edge: Optional[Edge] = None
        max_weight = float("-inf")
        for a, b in zip(path, path[1:]):
            weight = tree.weight(a, b)
            if weight > max_weight:
                max_weight = weight
                max_edge = canonical_edge(a, b)
        if max_edge is not None and new_weight < max_weight:
            tree.remove_edge(*max_edge)
            tree.add_edge(u, v, new_weight)
            return MSTUpdateResult(max_edge, canonical_edge(u, v), old_total, tree.total_weight())
        return MSTUpdateResult(None, None, old_total, tree.total_weight())

    # A tree edge became more expensive. Removing it creates a cut; choose the
    # cheapest road crossing that cut.
    tree.remove_edge(u, v)
    component_of = _components(tree)
    best: Optional[Tuple[str, str, float]] = None
    for a, b, weight in graph.edges():
        if component_of.get(a) != component_of.get(b):
            if best is None or weight < best[2]:
                best = (a, b, weight)
    if best is None:
        tree.add_edge(u, v, new_weight)
        raise ValueError("Road update disconnected the network")

    a, b, weight = best
    tree.add_edge(a, b, weight)
    added = canonical_edge(a, b)
    removed = canonical_edge(u, v)
    if added == removed:
        return MSTUpdateResult(None, None, old_total, tree.total_weight())
    return MSTUpdateResult(removed, added, old_total, tree.total_weight())


def find_augmenting_path(
    network: DirectedFlowNetwork, source: str, sink: str
) -> list[str]:
    """Return one residual-capacity path from source to sink using BFS."""
    queue = deque([source])
    parent: Dict[str, Optional[str]] = {source: None}
    while queue:
        node = queue.popleft()
        if node == sink:
            break
        for neighbor in network.residual_neighbors(node):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    if sink not in parent:
        return []

    path: list[str] = []
    cursor: Optional[str] = sink
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    return list(reversed(path))


def augment_once(network: DirectedFlowNetwork, source: str, sink: str) -> float:
    path = find_augmenting_path(network, source, sink)
    if not path:
        return 0.0
    bottleneck = min(network.residual_capacity(u, v) for u, v in zip(path, path[1:]))
    for u, v in zip(path, path[1:]):
        network.push(u, v, bottleneck)
    return bottleneck


def max_flow(network: DirectedFlowNetwork, source: str, sink: str) -> float:
    total = 0.0
    while True:
        added = augment_once(network, source, sink)
        if added == 0:
            return total
        total += added
