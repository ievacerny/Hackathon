"""Test the names module.

Written by Ieva and Arsalan
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


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "SW1"),
    (1, "SECOND_CLOCK"),
    (2, "DTYPE3"),
    (3, None),
    (-1, None)
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


# ------Tests below are written by Arsalan-------------------------
@pytest.mark.parametrize("name_string, number", [
    ("FIRST", 0),
    ("", 0),
    ("M11", 0),
])


def test_add_string(name_string, number):
    names = Names()
    assert names._add_name_string(name_string) == number


@pytest.mark.parametrize("name_string_1, number_1", [
    ("SECOND", 1),
    ("", 1),
    ("M40", 1),

])


def test_add_string_1(name_string_1, number_1):
    names = Names()
    names._add_name_string('initial')
    assert names._add_name_string(name_string_1) == number_1


@pytest.fixture
def names_list():
    return ['GATE5', 'NAND11', '4TEST']

def test_lookup(names_list):
    names = Names()
    assert names.lookup(names_list) == [0, 1, 2]


@pytest.fixture
def names_list_2():
    return []


def test_lookup_2(names_list_2):
    names = Names()
    assert names.lookup(names_list_2) == []


@pytest.fixture
def names_list_3():
    return ['GATE5', 'GATE5', 'GATE5', 'GATE5', 'GATE5', 'GATE5', 'GATE5', 'GATE5', 'GATE5']


def test_lookup_3(names_list_3):
    names = Names()
    assert names.lookup(names_list_3) == [0, 0, 0, 0, 0, 0, 0, 0, 0]
