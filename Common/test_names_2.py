import pytest

from names import Names


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





