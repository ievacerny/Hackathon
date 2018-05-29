"""Test the parse module.

Tests have been written for the lowest level parse_device, parse_connection and
parse_monitor functions. Further test cases can be added. Functions parse_list,
parse_section and the main one parse_network need to be tested. Manual testing
has been done with several different input file versions on the whole system.

For test case purposes, error message prints out the error code and message
first. Location of the error is printed later.

Written by Ieva
"""
import pytest
import operator

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def init_parser(data):
    """Write data to file and return an instance of parser."""
    with open('test_file.txt', 'w') as f:
        f.write(data)

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner("test_file.txt", names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser


@pytest.mark.parametrize("data, expected_error", [
    ("CLICK CL1 3,", "devices.BAD_DEVICE"),
    ("SW.TCH SW 0,", "devices.BAD_DEVICE"),
    ("nand N1 2,", "devices.BAD_DEVICE"),
    (".ND A! 2,", "devices.BAD_DEVICE"),
    (";R O1 2,", "devices.BAD_DEVICE"),
    (";", "devices.BAD_DEVICE"),
    ("-> DTYPE D1,", "devices.BAD_DEVICE"),
    ("NAND N! 2,", "devices.INVALID_QUALIFIER"),
    ("NAND , 2,", "INVALID_DEVICE_NAME"),
    ("NAND N1 2: NAND n2 2,", "MISSING_DELIMITER"),
    ("NAND N1 2 NAND N2 2,", "MISSING_DELIMITER"),
    ("NAND N1 2 nand n2 2,", "MISSING_DELIMITER")
])
def test_device_parsing(capsys, data, expected_error):
    """Test parse_device function."""
    parser = init_parser(data)  # FIXME Can I put this in a fixture somehow?
    # Get expected error message
    expected_error_code = operator.attrgetter(expected_error)(parser)
    expected_error_msg = parser.errors.error_msg[expected_error_code]
    # Check that parsing confirmed the existance of errors (should always work)
    assert not parser._parse_device()
    # Compare printed message with expected
    out, err = capsys.readouterr()
    assert out[:len(expected_error_msg)] == expected_error_msg


@pytest.mark.parametrize("data, expected_error", [
    ("SWITCH -> A1.I1,", "INVALID_DEVICE_NAME"),
    (". -> A1.I1,", "INVALID_DEVICE_NAME"),
    ("3 -> A1.I1,", "INVALID_DEVICE_NAME"),
    ("A1. -> SW1", "PORT_MISSING"),
    ("A1.! -> SW1", "INVALID_OUTPUT"),
    ("SW1 A1.I1", "MISSING_ARROW"),
    ("SW1 <- A1.I1", "MISSING_ARROW"),
    ("SW1 -> AND.I1", "INVALID_DEVICE_NAME"),
    ("SW1 -> ;", "INVALID_DEVICE_NAME")
])
def test_connection_parsing(capsys, data, expected_error):
    """Test parse_connection function."""
    parser = init_parser(data)
    # Add couple of devices
    [device_id_1, device_id_2] = parser.names.lookup(["SW1", "A1"])
    [device_type_1, device_type_2] = parser.names.lookup(["SWITCH", "AND"])
    parser.devices.make_device(device_id_1, device_type_1, 0)
    parser.devices.make_device(device_id_2, device_type_2, 2)
    # Get expected error message
    expected_error_code = operator.attrgetter(expected_error)(parser)
    expected_error_msg = parser.errors.error_msg[expected_error_code]
    # Check that parsing confirmed the existance of errors (should always work)
    assert not parser._parse_connection()
    # Compare printed message with expected
    out, err = capsys.readouterr()
    assert out[:len(expected_error_msg)] == expected_error_msg


@pytest.mark.parametrize("data, expected_error", [
    ("SWITCH,", "INVALID_DEVICE_NAME"),
    (".,", "INVALID_DEVICE_NAME"),
    ("3,", "INVALID_DEVICE_NAME"),
    ("A1.,", "PORT_MISSING"),
    ("A1.2,", "INVALID_OUTPUT"),
    ("SW1 A1", "MISSING_DELIMITER"),
    ("SW1:", "MISSING_DELIMITER"),
    ("A1.I1,", "INVALID_OUTPUT"),
])
def test_monitor_parsing(capsys, data, expected_error):
    """Test parse_monitor function."""
    parser = init_parser(data)
    # Add couple of devices
    [device_id_1, device_id_2] = parser.names.lookup(["SW1", "A1"])
    [device_type_1, device_type_2] = parser.names.lookup(["SWITCH", "AND"])
    parser.devices.make_device(device_id_1, device_type_1, 0)
    parser.devices.make_device(device_id_2, device_type_2, 2)
    # Get expected error message
    expected_error_code = operator.attrgetter(expected_error)(parser)
    expected_error_msg = parser.errors.error_msg[expected_error_code]
    # Check that parsing confirmed the existance of errors (should always work)
    assert not parser._parse_monitor()
    # Compare printed message with expected
    out, err = capsys.readouterr()
    assert out[:len(expected_error_msg)] == expected_error_msg
