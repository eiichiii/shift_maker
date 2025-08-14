from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Member:
    """Simple representation of a member."""

    name: str


class MemberAPI:
    """In-memory API to manage members."""

    def __init__(self) -> None:
        self._members: Dict[str, Member] = {}

    def add_member(self, name: str) -> Member:
        """Add a new member.

        Raises:
            ValueError: If the member already exists.
        """

        if name in self._members:
            raise ValueError("Member already exists")
        member = Member(name=name)
        self._members[name] = member
        return member

    def list_members(self) -> List[Member]:
        """Return all registered members."""

        return list(self._members.values())
