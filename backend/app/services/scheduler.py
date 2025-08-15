from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Set, Tuple
import calendar

try:
    import pulp
except Exception as exc:  # pragma: no cover - dependency resolution handled at runtime
    pulp = None  # type: ignore


@dataclass
class Member:
    """Representation of a member participating in the shift schedule."""

    id: int
    name: str
    gender: str  # expected values: 'M' or 'F'
    is_committee: bool
    preferred_days: Set[date] = field(default_factory=set)

    def is_available(self, day: date) -> bool:
        """Return True if the member is available on the given day."""
        return not self.preferred_days or day in self.preferred_days


def get_members_with_preferences(month: date) -> List[Member]:
    """Retrieve members and their preferred working days.

    This function is a stub meant to be replaced with actual data access logic.
    It should return members with their attributes and preferred days within the
    supplied month.
    """
    raise NotImplementedError("Data retrieval not implemented")


def _days_in_month(month: date) -> List[date]:
    """Return a list of all days in the month of the provided date."""
    _, last_day = calendar.monthrange(month.year, month.month)
    return [date(month.year, month.month, day) for day in range(1, last_day + 1)]


def generate_schedule(month: date) -> Dict[str, object]:
    """Generate an optimized shift schedule for the given month.

    The schedule follows several constraints:
    * Exactly four members per day.
    * At least one promotion committee member per day.
    * At least one male and one female per day.
    * No member works two consecutive days.

    Parameters
    ----------
    month: date
        Any date within the target month. Usually the first day of the month is
        supplied.

    Returns
    -------
    Dict[str, object]
        A dictionary containing the generated assignments, members that could
        not be assigned, and any violated constraints.
    """
    members = get_members_with_preferences(month)
    if pulp is None:
        raise RuntimeError("pulp library is required for schedule generation")

    days = _days_in_month(month)
    problem = pulp.LpProblem("shift_schedule", pulp.LpMinimize)

    # Decision variables: x[(member_id, day)] is 1 if member works on day
    x: Dict[Tuple[int, date], pulp.LpVariable] = {
        (m.id, d): pulp.LpVariable(f"x_{m.id}_{d.day}", cat="Binary")
        for m in members
        for d in days
    }

    # Objective: minimise total assignments (constant) to form a valid problem
    problem += pulp.lpSum(x.values())

    # Constraint: each day has exactly 4 members
    for d in days:
        problem += (
            pulp.lpSum(x[(m.id, d)] for m in members) == 4,
            f"staff_count_{d.day}",
        )

    # Constraint: at least one committee member per day
    for d in days:
        problem += (
            pulp.lpSum(x[(m.id, d)] for m in members if m.is_committee) >= 1,
            f"committee_{d.day}",
        )

    # Constraint: gender balance per day
    for d in days:
        problem += (
            pulp.lpSum(x[(m.id, d)] for m in members if m.gender == "M") >= 1,
            f"male_{d.day}",
        )
        problem += (
            pulp.lpSum(x[(m.id, d)] for m in members if m.gender == "F") >= 1,
            f"female_{d.day}",
        )

    # Constraint: avoid consecutive days for same member
    for m in members:
        for d1, d2 in zip(days[:-1], days[1:]):
            problem += (
                x[(m.id, d1)] + x[(m.id, d2)] <= 1,
                f"no_consecutive_{m.id}_{d1.day}",
            )

    # Constraint: respect member availability
    for m in members:
        for d in days:
            if not m.is_available(d):
                problem += (
                    x[(m.id, d)] == 0,
                    f"availability_{m.id}_{d.day}",
                )

    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))

    assignments: Dict[date, List[int]] = {d: [] for d in days}
    for m in members:
        for d in days:
            if pulp.value(x[(m.id, d)]) == 1:
                assignments[d].append(m.id)

    unassigned_members = [m.id for m in members if all(pulp.value(x[(m.id, d)]) != 1 for d in days)]

    violated_constraints: List[str] = []
    if pulp.LpStatus[status] != "Optimal":
        violated_constraints.append("solution_not_optimal")
    else:
        for d in days:
            staff = assignments[d]
            if len(staff) != 4:
                violated_constraints.append(f"staff_count_day_{d.day}")
            if not any(next((m for m in members if m.id == s and m.is_committee), None) for s in staff):
                violated_constraints.append(f"committee_day_{d.day}")
            if not any(next((m for m in members if m.id == s and m.gender == 'M'), None) for s in staff):
                violated_constraints.append(f"male_day_{d.day}")
            if not any(next((m for m in members if m.id == s and m.gender == 'F'), None) for s in staff):
                violated_constraints.append(f"female_day_{d.day}")

    return {
        "assignments": assignments,
        "unassigned_members": unassigned_members,
        "violated_constraints": violated_constraints,
    }
