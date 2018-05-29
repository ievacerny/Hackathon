"""Test the mynames module."""
import pytest

from scanner import Scanner
from names import Names

#scan = Scanner("scan_test_doc.txt", name)

@pytest.fixture
def init_scanner(data):
    with open('test_file_scanner.txt', 'w') as f:
        f.write(data)
    name = Names()
    #scan = Scanner('scan_test_doc.txt', name)
    scan = Scanner('test_file_scanner.txt', name)
    return scan

# def test_scanner_keyword(test_scanner):
#     assert test_scanner.get_symbol() == [3, 0]


@pytest.mark.parametrize("data, expected_output", [
    (',', [0, None]),
    (';', [1, None]),
    (':', [2, None]),
    ('NAND', [3, None]),
    ('DEVICES',[3, 0]),
    ('CONNECTIONS',[3, 1]),
    ('7', [4, 7]),
    ('SW1', [5,3]),
    ('->', [6, None]),
    ('', [7, None]),
    ('.', [9, None]),

])


def test_scanning(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.get_symbol() == expected_output


@pytest.mark.parametrize("data, expected_output", [
    ('109', 109),
    ('60', 60),
    ('463 ', 463),
    ('410asdfg', 410),
    ('407-', 407),
    ('612.', 612),
    ('154,', 154),
    ('157;.plp', 157)

])

def test_get_number(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.get_number() == expected_output

@pytest.mark.parametrize("data, expected_output", [
    ('PART', 'PART'),
    ('CLK', 'CLK'),
    ('FOUR1', 'FOUR1'),
    ('X26', 'X26'),
    ('CT ', 'CT'),
    ('SW4.3', 'SW4'),
    ('BTD5_I', 'BTD5'),
    ('AH4;BST', 'AH4'),


])

def test_get_name(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.get_name() == expected_output

@pytest.mark.parametrize("data, expected_output", [

    ('abcdef', 'b'),
    ('45678', '5'),
    (',.-l', '.'),
    ('l dac', ' '),

])

def test_advance(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.advance() == expected_output





