from typing import Dict, Iterable, List

from .member_api import Member


def generate_shifts(
    members: List[Member],
    days: Iterable[str],
    max_shifts_per_member: int = 1,
) -> Dict[str, Member]:
    """Assign members to days respecting a maximum per member.

    Args:
        members: Members available for shifts.
        days: Iterable of day identifiers.
        max_shifts_per_member: Maximum shifts allowed per member.

    Returns:
        Mapping of day to assigned member.

    Raises:
        ValueError: If assignments cannot be made.
    """

    members = list(members)
    if not members:
        raise ValueError("No members provided")

    schedule: Dict[str, Member] = {}
    counts: Dict[str, int] = {m.name: 0 for m in members}
    idx = 0
    for day in days:
        # Find next available member respecting the max limit
        available = [m for m in members if counts[m.name] < max_shifts_per_member]
        if not available:
            raise ValueError("No available member for assignment")
        member = available[idx % len(available)]
        schedule[day] = member
        counts[member.name] += 1
        idx += 1
    return schedule
