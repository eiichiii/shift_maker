import pytest

from ..member_api import MemberAPI


def test_add_and_list_members():
    api = MemberAPI()
    api.add_member("Alice")
    api.add_member("Bob")
    names = [m.name for m in api.list_members()]
    assert names == ["Alice", "Bob"]


def test_add_member_duplicate():
    api = MemberAPI()
    api.add_member("Alice")
    with pytest.raises(ValueError):
        api.add_member("Alice")
