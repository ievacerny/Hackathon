"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
"""

import re
import sys

class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into
    symbol types and symbol IDs that the parser can use. It also skips over
    comments and irrelevant formatting characters, such as spaces and line
    breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters and
                      returns the symbol type and ID.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try:
            input_file = open(path, 'r')
        except FileNotFoundError:
            print("File doesn't exist")
            sys.exit()

        re.sub('/[^>]+/', '', input_file)

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.COLON,
                                 self.KEYWORD, self.NUMBER, self.NAME, self.ARROW] = range(7)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR", "DTYPE", "XOR", "AND", "NAND", "OR", "NOR", "SWITCH",
                              "CLOCK"]
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""

    def advance(self):
        char = input_file.read(1)
        self.current_character = char
        return char

    def skip_spaces(self):
        while True:
            char = input_file.read(1)
            if not char.isspace():
                self.current_character = char
                return char
            else:
                continue

    def get_name(self):
        name = ''
        while True:
            char = input_file.read(1)
            if char == '':
                break
            if char.isalpha():
                name = char
                break

        while True:
            nextchar = input_file.read(1)
            if nextchar.isalnum() == True:
                name = name + nextchar
                continue
            else:
                self.current_character = next_char
                break
        return name

    def get_number(self):
        number = ""
        while True:
            char = file.read(1)
            if char == '':
                break
            if char.isdigit():
                number = char
                break

        while True:
            nextchar = file.read(1)
            if nextchar.isdigit() == True:
                number = number + nextchar
                continue
            else:
                self.current_character = nextchar
                break

    def get_symbol(self):
        """Return the symbol type and ID of the next sequence of characters.

        If the current character is not recognised, both symbol type and ID
        are assigned None. Note: this function is called again (recursively)
        if it encounters a comment or end of line.
        """

        def get_symbol(self):
            """Return the symbol type and ID of the next sequence of characters."""

            self.skip_spaces()  # current character now not whitespace

            if self.current_character.isalpha():  # name
                name_string = self.get_name()

                if name_string in self.keywords_list:
                    symbol_type = self.KEYWORD

                else:
                    symbol_type = self.NAME
                    [symbol_id] = self.names.lookup([name_string])

            elif self.current_character.isdigit():  # number
                symbol_id = self.get_number()
                symbol_type = self.NUMBER

            elif self.current_character == ",":
                symbol_type = self.COMMA
                symbol_id = None
                self.advance()

            elif self.current_character == ";":
                symbol_type = self.SEMICOLON
                symbol_id = None
                self.advance()

            elif self.current_character == ":":
                symbol_type = self.COLON
                symbol_id = None
                self.advance()

            elif self.current_character == "-":
                symbol_type = self.ARROW
                symbol_id = None
                self.advance()
                self.advance()

            else:  # not a valid character
                symbol_type = None
                symbol_id = None
                self.advance()

            return [symbol_type, symbol_id]