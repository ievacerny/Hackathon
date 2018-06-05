"""Test the parse module.

Tests have been written for the lowest level parse_device, parse_connection and
parse_monitor functions. Further test cases can be added. Functions parse_list,
parse_section and the main one parse_network need to be tested. Manual testing
has been done with several different input file versions on the whole system.

For test case purposes, error message prints out the error code and message
first. Location of the error is printed later.

Written by Ieva and Mark
"""
import pytest
import operator

import gettext
gettext.install('logsim')

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


@pytest.mark.parametrize("file, expected_return", [
    ("def_files/parser_test_file.txt", False),
    ("def_files/parser_test_file1.txt", True),
    ("def_files/parser_test_file2.txt", False),
    ("def_files/parser_test_file3.txt", True)
])
def test_correct_parsing(file, expected_return):
    """Test if parser distinguishes between bad and good definition files."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(file, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parsed_succesfully = parser.parse_network()
    assert parsed_succesfully is expected_return


# ------Tests below are written by Mark-------------------------


@pytest.mark.parametrize("data, expected_error", [
    ("","PREMATURE_EOF"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2", "PREMATURE_EOF"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2,", "PREMATURE_EOF"),
    ("SWITCH s1 0, SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2","NO_DEVICE_KEYWORD"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; s1->n1.I1,s2->n1.I2;", "NO_CONNECTIONS_KEYWORD"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2;;", "NO_MONITOR_KEYWORD"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS s1->n1.I1,s2->n1.I2;", "MISSING_COLON"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2; MONITOR:;", "INVALID_DEVICE_NAME"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2 CONNECTIONS: s1->n1.I1,s2->n1.I2;", "MISSING_DELIMITER"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1.->d1.DATA;", "PORT_MISSING"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1.DSF->d1.DATA;", "INVALID_OUTPUT"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1.Q->d1.DSF;", "INVALID_INPUT"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1.Q d1.DATA;", "MISSING_ARROW"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1.Q->d1.DATA;", "NOT_ALL_INPUTS_CONNECTED"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2, CONNECTIONS: s1->n1.I1,s2->n1.I2;", "COMMA_NOT_SEMICOLON"),
    ("DEVICES: SWITCH s1 -3,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I2;", "devices.INVALID_QUALIFIER"),
    ("DEVICES:;CONNECTIONS:;","devices.BAD_DEVICE"),
    ("DEVICES: DTYPE d1 0; CONNECTIONS: d1.Q->d1.DATA;", "devices.QUALIFIER_PRESENT"),
    ("DEVICES: DTYPE d1, NAND d1; CONNECTIONS: d1.Q->d1.DATA;", "devices.DEVICE_PRESENT"),
    ("DEVICES: AND a1 2, SWITCH sw1 0; CONNECTIONS: sw1->a1.I1, sw1->a1.I2; MONITOR: a1,a1;", "monitors.MONITOR_PRESENT"),
    ("DEVICES: SWITCH s1 0, DTYPE d1; CONNECTIONS: d1->d1.DATA;", "network.PORT_ABSENT"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1;", "network.OUTPUT_TO_OUTPUT"),
    ("DEVICES: SWITCH s1 0,SWITCH s2 0,NAND n1 2; CONNECTIONS: s1->n1.I1,s2->n1.I1;", "network.INPUT_CONNECTED"),

    #New tests for NOT
    ("DEVICES: SWITCH s1 0, NO n1; CONNECTIONS: s1->n1.;", "devices.BAD_DEVICE"),
    ("DEVICES: SWITCH s1 0, NOTD n1; CONNECTIONS: s1->n1.;", "devices.BAD_DEVICE"),
    ("DEVICES: SWITCH s1 0, NOT n1 324; CONNECTIONS: s1->n1.I1;", "devices.QUALIFIER_PRESENT"), #fail
    ("DEVICES: SWITCH s1 0, NOT n1 asd; CONNECTIONS: s1->n1.I1;", "MISSING_DELIMITER"), 
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1;", "network.OUTPUT_TO_OUTPUT"), 
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1.I2;", "INVALID_INPUT"),
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1.I;", "INVALID_INPUT"),
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1.;", "PORT_MISSING"),
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1.I1; MONITOR: n1.I1", "INVALID_OUTPUT"),

    #New tests for RC
    ("DEVICES: SWITCH s1 0, R r1; CONNECTIONS: ;", "devices.BAD_DEVICE"),
    ("DEVICES: SWITCH s1 0, RCA r1; CONNECTIONS: ;", "devices.BAD_DEVICE"),
    ("DEVICES: SWITCH s1 0, RC r1; CONNECTIONS: ;", "devices.INVALID_QUALIFIER"),
    ("DEVICES: SWITCH s1 0, RC; CONNECTIONS: ;", "INVALID_DEVICE_NAME"),
    ("DEVICES: SWITCH s1 0, RC r1 0; CONNECTIONS: ;", "devices.INVALID_QUALIFIER"),
    ("DEVICES: SWITCH s1 0, RC r1 adas; CONNECTIONS: ;", "devices.INVALID_QUALIFIER"),
    ("DEVICES: SWITCH s1 0, RC r1 5; CONNECTIONS: s1->r1;", "network.OUTPUT_TO_OUTPUT"),
    ("DEVICES: SWITCH s1 0, RC r1 5; CONNECTIONS: s1->r1.I1;", "INVALID_INPUT"),
    ("DEVICES: SWITCH s1 0, RC r1 5, NAND n1 2; CONNECTIONS: r1.Q->n1.I1, s1->n1.I2;", "INVALID_OUTPUT"),
    ("DEVICES: SWITCH s1 0, RC r1 5, NAND n1 2; CONNECTIONS: r1.->n1.I1, s1->n1.I2;", "PORT_MISSING"),
    ("DEVICES: SWITCH s1 0, RC r1 5, NAND n1 2; CONNECTIONS: r1->n1.I1, s1->n1.I2; MONITOR: r1.I", "INVALID_OUTPUT")
])


def test_network_parsing_fail(capsys, data, expected_error):
    """Test parse_network function."""
    parser = init_parser(data)

    # Get expected error message
    expected_error_code = operator.attrgetter(expected_error)(parser)
    expected_error_msg = parser.errors.error_msg[expected_error_code]

    assert not parser.parse_network()
    # Compare printed message with expected
    out, err = capsys.readouterr()
    assert out[:len(expected_error_msg)] == expected_error_msg


@pytest.mark.parametrize("data", [
    ("DEVICES: SWITCH s1 0, NOT n1; CONNECTIONS: s1->n1.I1;"),
    ("DEVICES: SWITCH s1 1, NOT n1; CONNECTIONS: s1->n1.I1;"),
    ("DEVICES: NOT n1, RC r1 5; CONNECTIONS: r1->n1.I1; MONITOR: n1;"),
    ("DEVICES: SWITCH s1 1, RC r1 5, NOT n2, NAND n1 2; CONNECTIONS: r1->n1.I1, s1->n1.I2, n1->n2.I1;")
])


def test_network_parsing_pass(capsys, data):
    """Test parse_network function."""
    parser = init_parser(data)

    assert parser.parse_network()
