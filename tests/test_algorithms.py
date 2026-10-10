import unittest

from relief_planner.allocation import exact_load_bottom_up, exact_load_top_down
from relief_planner.graph import DirectedFlowNetwork, WeightedUndirectedGraph
from relief_planner.locations import closest_location, qwerty_edit_distance
from relief_planner.network import max_flow, minimum_spanning_tree, update_mst_for_weight_change
from relief_planner.teams import split_incompatible_teams


class NetworkTests(unittest.TestCase):
    def test_dynamic_mst_update(self):
        graph = WeightedUndirectedGraph()
        for u, v, w in [("A", "B", 1), ("B", "C", 2), ("A", "C", 5)]:
            graph.add_edge(u, v, w)
        tree = minimum_spanning_tree(graph)
        self.assertEqual(tree.total_weight(), 3)
        result = update_mst_for_weight_change(graph, tree, ("A", "C"), 1)
        self.assertEqual(tree.total_weight(), 2)
        self.assertIsNotNone(result.removed_edge)

    def test_max_flow(self):
        network = DirectedFlowNetwork()
        for u, v, c in [("S", "A", 4), ("S", "B", 3), ("A", "T", 4), ("B", "T", 3)]:
            network.add_edge(u, v, c)
        self.assertEqual(max_flow(network, "S", "T"), 7)


class AllocationTests(unittest.TestCase):
    def test_bottom_up_load(self):
        result = exact_load_bottom_up([2, 7, 11, 13], 20)
        self.assertEqual(sum(result), 20)

    def test_top_down_load(self):
        result = exact_load_top_down([2, 7, 11, 13], 18)
        self.assertEqual(sum(result), 18)


class TeamTests(unittest.TestCase):
    def test_bipartite_split(self):
        feasible, a, b = split_incompatible_teams({"A": {"B"}, "B": {"A", "C"}, "C": {"B"}})
        self.assertTrue(feasible)
        self.assertFalse(({"A", "B"} <= a) or ({"A", "B"} <= b))

    def test_odd_cycle_rejected(self):
        feasible, _, _ = split_incompatible_teams({"A": {"B", "C"}, "B": {"A", "C"}, "C": {"A", "B"}})
        self.assertFalse(feasible)


class LocationTests(unittest.TestCase):
    def test_closest_location(self):
        name, score = closest_location("sheltrr", ["clinic", "shelter", "warehouse"])
        self.assertEqual(name, "shelter")
        self.assertGreaterEqual(score, 0)

    def test_exact_match_zero(self):
        self.assertEqual(qwerty_edit_distance("depot", "depot"), 0)


if __name__ == "__main__":
    unittest.main()
