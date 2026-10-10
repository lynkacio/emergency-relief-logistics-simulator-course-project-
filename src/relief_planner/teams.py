from __future__ import annotations

from collections import deque
from typing import Mapping, Set, Tuple


def split_incompatible_teams(
    conflicts: Mapping[str, Set[str]],
) -> Tuple[bool, set[str], set[str]]:
    """Split workers into two teams so no conflicting pair shares a team.

    This is a bipartite-graph (two-colouring) problem solved with BFS.
    """
    people = set(conflicts)
    for neighbors in conflicts.values():
        people.update(neighbors)

    colour: dict[str, int] = {}
    for start in people:
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            person = queue.popleft()
            for other in conflicts.get(person, set()):
                if other not in colour:
                    colour[other] = 1 - colour[person]
                    queue.append(other)
                elif colour[other] == colour[person]:
                    return False, set(), set()

    team_a = {person for person, side in colour.items() if side == 0}
    team_b = people - team_a
    return True, team_a, team_b
