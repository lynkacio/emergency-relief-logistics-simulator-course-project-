from __future__ import annotations

import argparse
from pathlib import Path

from .simulator import load_scenario, run_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emergency Relief Logistics Planning Simulator")
    parser.add_argument("scenario", type=Path, help="Path to a scenario JSON file")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = run_scenario(load_scenario(args.scenario))

    print("=== Emergency Relief Logistics Report ===")
    print(f"Initial minimum road-network cost: {report.initial_road_cost:.1f}")
    print(f"Updated minimum road-network cost: {report.updated_road_cost:.1f}")
    print(f"Maximum transport capacity: {report.max_transport_capacity:.1f}")
    print(f"Selected vehicle load: {report.selected_load} (total={sum(report.selected_load)})")
    print(f"Relief team A: {sorted(report.team_a)}")
    print(f"Relief team B: {sorted(report.team_b)}")
    print(f"Corrected location: {report.corrected_location}")


if __name__ == "__main__":
    main()
