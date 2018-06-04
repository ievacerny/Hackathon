#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx
import gettext
# Set default to English for imports
gettext.install('logsim')

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = _("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path> [lang=<language code>]\n"
                     "Graphical user interface: logsim.py <file path> [lang=<language code>]")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print(_("Error: Invalid command line arguments.\n"))
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)


    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        l = None

        if len(arguments) == 1:
            [path] = arguments
        elif len(arguments) == 2:
            [path, language] = arguments
            l = language.split('=')
        else:  # wrong number of arguments
            print(_("Error: Only the file path and the language can be specified.\n"))
            print(usage_message)
            sys.exit()

        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        
        # Set language (English is already installed, change if needed)
        if l is None:
            pass
        elif len(l) != 2 or l[0] != 'lang':
            print(_("Error: Language specified incorrectly. Specify using 'lang=<language code>'"))
            print(_("Language will default to English."))
        elif l[1] == 'el':
            el = gettext.translation('logsim', localedir='wx/locale', languages=['el'])
            el.install()
        elif l[1] != 'en':
            print(_("Error: Unknown language code. Supported languages: 'en' (English), 'el' (Greek)."))
            print(_("Language will default to English."))
        
        if parser.parse_network():
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()


if __name__ == "__main__":
    
    main(sys.argv[1:])
