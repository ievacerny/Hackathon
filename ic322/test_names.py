"""Test the names module.

Written by Ieva
"""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["SW1", "SECOND_CLOCK", "DTYPE3"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    names = Names()
    names.lookup(name_string_list)
    return names


def test_get_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "SW1"),
    (1, "SECOND_CLOCK"),
    (2, "DTYPE3"),
    (3, None)
])
def test_get_name_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


@pytest.mark.parametrize("name_string, expected_id", [
    ("SW1", 0),
    ("SECOND_CLOCK", 1),
    ("DTYPE3", 2),
    ("CLOCK", None)
])
def test_query(used_names, new_names, name_string, expected_id):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.query(name_string) == expected_id
    # Name is absent
    assert new_names.query(name_string) is None
