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
    ('NAND', [3, 6]),
    ('DEVICES',[3, 0]),
    ('CONNECTIONS',[3, 1]),
    ('7', [4, 7]),
    ('SW1', [5,11]),
    ('->', [6, None]),
    ('', [7, None]),
    ('.', [9, None]),
    ('?', [None, None]),
    ('\\*7*\\.', [9, None]),
    ('\\*7*\\\\', [None, None]),
    ('''\\\\fsdfsdf\nDEVICES''', [3, 0]),
    ('\\', [None, None]),
    ('1BC', [4, 1]),
    ('--', [None, None]),
    ('-->', [None, None]),
    ('<-', [None, None]),
    ('\\ABC', [None, None]),
    ('B1C', [5, 11]),
    ('*\\', [None, None]),
    ('\\\\ \n\\', [None, None]),
    ('\\\\ \n\\*ABC*\\.', [9, None]),
    ('\\\\ \n\\*ABC*\\\\', [None, None]),
    ('\\\\ \n\\*A\\\\BC*\\.', [9, None]),
    ('\\\\ \n\\*A*BC*\\ .', [9, None]),
    ('\\\\ \n\\*A\\BC*\\\t.', [9, None]),
    ('\\\\ \n\\*A\\\\BC**\\.', [9, None]),
    ('\\\\ \n\\*A\\\\BC\\*\\.', [9, None]),
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
    ('157;.plp', 157),
    ('15:17', 15),
    ('asd15', -1),
    ('\n  15', 15),
    ('\n sfd15', -1)
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
    ('\n  12395', ''),
    ('\n\t\rABC', 'ABC'),
    ('2ABC', ''),
])

def test_get_name(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.get_name() == expected_output

@pytest.mark.parametrize("data, expected_output", [

    ('abcdef', 'b'),
    ('45678', '5'),
    (',.-l', '.'),
    ('l dac', ' '),
    ('\n   12', '2'),
    ('', '')
])

def test_advance(data, expected_output):
    scanner = init_scanner(data)
    assert scanner.advance() == expected_output


@pytest.mark.parametrize("data, expected_output", [
    ('ABC:DEVICES 24;',
        [[5, 11], [2, None], [3, 0], [4, 24], [1, None]]),
    ('''\\\\Comment\nDEVICES: SW1 -> A1''',
        [[3, 0], [2, None], [5, 11], [6, None], [5, 12]]),
    ('''\\\\Comment\nCONNECTION: SW1 -> A1''',
        [[5, 11], [2, None], [5, 12], [6, None], [5, 13]]),
    ('''\\*Comment*\\DEVICES: SW1 -> A1''',
        [[3, 0], [2, None], [5, 11], [6, None], [5, 12]]),
    ('NAND N! 4,',
        [[3, 6], [5, 11], [None, None], [4, 4], [0, None]]),
    ('\t123\nABC\rDEF\t\n\rDEVICES :',
        [[4, 123], [5, 11], [5, 12], [3, 0], [2, None]]),
    ('''\\*Comment\n*\\DEVICES: SW1 -> A1''',
        [[3, 0], [2, None], [5, 11], [6, None], [5, 12]]),
    ('''\\*Comment\n\\\\anothercomment*\\DEVICES: SW1 -> A1''',
        [[3, 0], [2, None], [5, 11], [6, None], [5, 12]])
])
def test_symbol_sequence(data, expected_output):
    """Test if a sequence of symbols is correct."""
    scanner = init_scanner(data)
    symbols = []
    for i in range(5):
        symbols.append(scanner.get_symbol())
    assert symbols == expected_output


@pytest.mark.parametrize(
    "data, expected_output, error_prev_symb, no_arrow, err_loc", [
        ("DEVICES:\nCLOCK CL3 3,", "CLOCK CL3 3,\n",
            False, True, 4),
        ("DEVICES:\nCLOCK\nCL3\n3,", "CL3\n",
            False, True, 4),
        ("DEVICES:\nCLOCK\n\tCL3\n3,", "\tCL3\n",
            False, True, 4),
        ("DEVICES:\nCLOCK\n\n\n\tCL3\n3,", "\tCL3\n",
            False, True, 4),
        ("DEVICES:\nCLOCK CL3 3,", "CLOCK CL3 3,\n        ^\n",
            False, False, 4),
        ("DEVICES:\n\tCLOCK CL3 3,", "\tCLOCK CL3 3,\n\t        ^\n",
            False, False, 4),
        ("DEVICES:\nCLOCK\n\nCL3 3,", "CL3 3,\n  ^\n",
            False, False, 4),
        ("DEVICES:\nCLOCK CL3 3,", "CLOCK CL3 3,\n    ^\n",
            True, False, 4),
        ("DEVICES:\nCLOCK\tCL3 3,", "CLOCK\tCL3 3,\n    ^\n",
            True, False, 4),
        ("DEVICES:\n\tCLOCK\tCL3 3,", "\tCLOCK\tCL3 3,\n\t    ^\n",
            True, False, 4),
        ("DEVICES:\nCLOCK  .  CL3 3,", "CLOCK  .  CL3 3,\n       ^\n",
            True, False, 5),
        ("DEVICES:\nCLOCK \*Com*\ CL3 3,", "CLOCK \*Com*\ CL3 3,\n    ^\n",
            True, False, 4),
        ("DEVICES:\n\tCLOCK \*Com*\ CL3 3,",
            "\tCLOCK \*Com*\ CL3 3,\n\t    ^\n",
            True, False, 4),
        ("DEVICES:\n\tCLOCK\t\*Com*\CL3 3,",
            "\tCLOCK\t\*Com*\CL3 3,\n\t    ^\n",
            True, False, 4),
        ("DEVICES:\n\tCLOCK\*\tCom*\CL3 3,",
            "\tCLOCK\*\tCom*\CL3 3,\n\t    ^\n",
            True, False, 4),
        ("DEVICES:\nCLOCK \*CLOCK*\ CL3 3,", "CLOCK \*CLOCK*\ CL3 3,\n    ^\n",
            True, False, 4),
        ("DEVICES:\nCLOCK *CLOCK* CL3 3,",
            "CLOCK *CLOCK* CL3 3,\n            ^\n",
            True, False, 7),
        ("DEVICES:\nCLOCK \CLOCK\ CL3 3,",
            "CLOCK \CLOCK\ CL3 3,\n            ^\n",
            True, False, 7),
        ("DEVICES:\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
            True, False, 3),
        ("DEVICES:\n\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
            True, False, 3),
        ("\tDEVICES:\nCLOCK CL3 3,", "\tDEVICES:\n\t       ^\n",
            True, False, 3),
        ("DEVICES:\n\\\\Comment\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
            True, False, 3),
        ("DEVICES:\n\\\nCLOCK CL3 3,", "\\\n^\n",
            True, False, 4),
        ("DEVICES:\n\\Comm\nCLOCK CL3 3,", "\\Comm\n    ^\n",
            True, False, 5),
        ("DEVICES:\\*Com\nment\n*\\CLOCK CL3 3,", "DEVICES:\\*Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\\*Com\nment\n*CLOCK *\\CLOCK CL3 3,",
            "DEVICES:\\*Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\\*Com\nment\n\\CLOCK *\\CLOCK CL3 3,",
            "DEVICES:\\*Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\\*Com\nment\n\\CLOCK *\\CLOCK*\\ CL3 3,",
            "\\CLOCK *\\CLOCK*\\ CL3 3,\n               ^\n",
            True, False, 6),
        ("DEVICES:\\*Com\\*\nment\n\\CLOCK *\\CLOCK*\\ CL3 3,",
            "\\CLOCK *\\CLOCK*\\ CL3 3,\n               ^\n",
            True, False, 6),
        ("DEVICES:\\*Com\nment\n\\CLOCK *\\*\\CLOCK CL3 3,",
            "DEVICES:\\*Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\\*C\nom\n\n*\\CLOCK CL3 3,", "DEVICES:\\*C\n       ^\n",
            True, False, 3),
        ("DEVICES:\n\\\\DEVICES:com\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
            True, False, 3),
        ("DEVICES:\n\\\\DEVICES:com\n\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
            True, False, 3),
        ("\\*C\nom*\\DEVICES:\nCLOCK CL3 3,",
            "om*\\DEVICES:\n           ^\n",
            True, False, 3),
        ("DEVICES:\\*Com\nment\n*\\CLOCK CL3 3,", "DEVICES:\\*Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\n*Comm\n*CLOCK CL3 3,", "*CLOCK CL3 3,\n^\n",
            True, False, 6),
        ("DEVICES:\n*Comm\n*CLOCK CL3 3,", "*Comm\n    ^\n",
            True, False, 5),
        ("DEVICES:\\\\Com\nCLOCK CL3 3,", "DEVICES:\\\\Com\n       ^\n",
            True, False, 3),
        ("DEVICES:\\\\*Com\nCLOCK CL3 3,", "DEVICES:\\\\*Com\n       ^\n",
            True, False, 3)
    ]
)
def test_get_line(capsys, data, expected_output, error_prev_symb,
                  no_arrow, err_loc):
    """Test printing out of the error line function."""
    scanner = init_scanner(data)
    for i in range(err_loc):
        scanner.get_symbol()
    scanner.get_line(error_prev_symb, no_arrow)
    out, err = capsys.readouterr()
    assert out == expected_output, scanner.current_symbol
