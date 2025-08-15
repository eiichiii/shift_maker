import pytest

from ..member_api import MemberAPI
from ..shift_service import generate_shifts


def test_generate_shifts_respects_constraints():
    api = MemberAPI()
    api.add_member("Alice")
    api.add_member("Bob")
    members = api.list_members()
    days = ["Mon", "Tue", "Wed", "Thu"]
    schedule = generate_shifts(members, days, max_shifts_per_member=2)
    counts = {m.name: 0 for m in members}
    for day, member in schedule.items():
        counts[member.name] += 1
    assert set(schedule.keys()) == set(days)
    assert all(count <= 2 for count in counts.values())


def test_generate_shifts_raises_with_insufficient_members():
    api = MemberAPI()
    api.add_member("Alice")
    members = api.list_members()
    days = ["Mon", "Tue"]
    with pytest.raises(ValueError):
        generate_shifts(members, days)
