from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .allocation import exact_load_bottom_up
from .graph import DirectedFlowNetwork, WeightedUndirectedGraph
from .locations import closest_location
from .network import max_flow, minimum_spanning_tree, update_mst_for_weight_change
from .teams import split_incompatible_teams


@dataclass
class ScenarioReport:
    initial_road_cost: float
    updated_road_cost: float
    max_transport_capacity: float
    selected_load: list[int]
    team_a: set[str]
    team_b: set[str]
    corrected_location: str


def load_scenario(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_scenario(data: dict[str, Any]) -> ScenarioReport:
    roads = WeightedUndirectedGraph()
    for item in data["roads"]:
        roads.add_edge(item["from"], item["to"], item["cost"])

    mst = minimum_spanning_tree(roads)
    initial_cost = mst.total_weight()

    change = data["road_cost_change"]
    update_mst_for_weight_change(
        roads,
        mst,
        (change["from"], change["to"]),
        change["new_cost"],
    )

    transport = DirectedFlowNetwork()
    for item in data["transport_routes"]:
        transport.add_edge(item["from"], item["to"], item["capacity"])
    transport_capacity = max_flow(transport, data["flow_source"], data["flow_sink"])

    selected_load = exact_load_bottom_up(data["supply_weights"], data["vehicle_capacity"])

    conflicts = {name: set(values) for name, values in data["team_conflicts"].items()}
    feasible, team_a, team_b = split_incompatible_teams(conflicts)
    if not feasible:
        team_a, team_b = set(), set()

    corrected, _ = closest_location(data["typed_location"], data["known_locations"])

    return ScenarioReport(
        initial_road_cost=initial_cost,
        updated_road_cost=mst.total_weight(),
        max_transport_capacity=transport_capacity,
        selected_load=selected_load,
        team_a=team_a,
        team_b=team_b,
        corrected_location=corrected,
    )
