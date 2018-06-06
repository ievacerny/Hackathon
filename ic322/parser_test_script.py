"""Basic script to run the parser.

If debug logging is needed, change self.log flag in Parser class to True.
"""
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

n = Names()
d = Devices(n)
net = Network(n, d)
m = Monitors(n, d, net)
s = Scanner("parser_test_file.txt", n)
parser = Parser(n, d, net, m, s)
parser.parse_network()
