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
])

def test_network_parsing(capsys, data, expected_error):
    """Test parse_network function."""
    parser = init_parser(data) 

    # Get expected error message
    expected_error_code = operator.attrgetter(expected_error)(parser)
    expected_error_msg = parser.errors.error_msg[expected_error_code]
    
    assert not parser.parse_network()
    # Compare printed message with expected
    out, err = capsys.readouterr()
    assert out[:len(expected_error_msg)] == expected_error_msg



