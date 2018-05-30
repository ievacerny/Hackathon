"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
"""

import sys
# import re


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
            self.input_file = open(path, 'r')
        except FileNotFoundError:
            print("Filename incorrect or file doesn't exist")
            sys.exit()

        # self.input_file = open(path, 'r')
        self.list_file = [line.rstrip('\n') for line in open(path, 'r')]

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.COLON,
                                 self.KEYWORD, self.NUMBER, self.NAME, self.ARROW, self.EOF, self.NEWLINE, self.DOT] = range(10)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR", "DTYPE", "XOR", "AND", "NAND", "OR", "NOR", "SWITCH",
                              "CLOCK"]
        dummy = self.names.lookup(self.keywords_list)
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list[:3])
        self.current_character = ""
        self.name_string = ''
        self.character_count = -1
        self.line_count = 0
        self.current_symbol = ''
        self.prev_symbol = ''
        self.two_prev_symbol = ''
        self.space_count = 0
        self.advance()
        self.skip_spaces()

    def advance(self):
        char = self.input_file.read(1)
        self.character_count += 1
        self.current_character = char
        return char

    def skip_spaces(self):
        self.space_count = 0
        while self.current_character.isspace():
            if self.current_character == "\n":
                self.character_count = -1
                # print("Reser in skip spaces: {}".format(self.character_count))
                self.line_count += 1
            self.space_count += 1
            self.current_character = self.input_file.read(1)
            self.character_count += 1
            # print("Skip spaces {}".format(self.character_count))
            # print(self.character_count)

    def get_name(self):
        name = ''
        if self.current_character.isalpha():
            name = self.current_character

        while True:
            nextchar = self.input_file.read(1)
            self.character_count += 1
            # print("Names: {}".format(self.character_count))
            if nextchar.isalnum():
                name = name + nextchar
                continue
            else:
                self.current_character = nextchar
                break
        return name

    def cur_sym(self):
        print(self.current_symbol)

    def get_line(self, before, arrow):  # arrow true means no arrow
        # length = len(self.current_symbol)
        # if self.current_symbol == self.list_file[self.line_count][:length] and self.line_count != 0:

        # if before == True and self.line_count != 0:
        #     prev_line = self.list_file[self.line_count - 1]
        #     prev_symbol = self.prev_symbol
        #     print(prev_line)
        #     print(' ' * (prev_line.find(prev_symbol) - 1), '^')

        if before is True and arrow is False:
            symbol = self.current_symbol
            line = self.list_file[self.line_count]
            prev_symbol = self.prev_symbol
            # prev_line = self.list_file[self.line_count - 1]
            prev_line_index = self.line_count - 1
            while self.list_file[prev_line_index].isspace() is True or len(self.list_file[prev_line_index]) == 0:
                prev_line_index -= 1
            while (self.list_file[prev_line_index]).find('\\\\') != -1 or (self.list_file[prev_line_index]).find('\\*') or (self.list_file[prev_line_index]).find('*\\'):
                prev_line_index -= 1
            prev_line = self.list_file[prev_line_index]

            # len(re.findall(check_string, test_string))

            # if len(re.findall(line, symbol)) == 1:
            #     if line.find(symbol) == 0:
            #         print(prev_line)
            #         print(' ' * (prev_line.find(prev_symbol) - 1), '^')
            #
            #     else:
            #         print(line)
            #         print(' ' * (line.find(prev_symbol) - 1), '^')

            if line.find(symbol) == 0:
                print(prev_line)
                print(' ' * (len(prev_line)-1), '^')

            else:
                symb_len = len(symbol)
                prev_symb_len = len(prev_symbol)
                # print(symb_len)
                # print("Index {}".format(self.character_count - symb_len - 1))

                print(line)
                print(' '*(self.character_count - symb_len - 1 - prev_symb_len - self.space_count), '^')

        elif before is False and arrow is True:
            line = self.list_file[self.line_count]
            print(line)

        elif before is False and arrow is False:
            # print(self.character_count)
            line = self.list_file[self.line_count]
            # symbol = self.current_symbol
            character_no = self.character_count
            print(line)
            # print(' ' * (character_no - 2), '^')
            cut_line = line[:character_no - 2]
            arrow_line = ''
            for char in cut_line:
                if not char.isspace():
                    arrow_line = arrow_line + ' '
                else:
                    arrow_line = arrow_line + char
            print(arrow_line, '^')
        # else:
        #     line = self.list_file[self.line_count]
        #     symbol = self.current_symbol
        #
        #     print(line)
        #     print(' ' * (line.find(symbol)-1), '^')

        # print(len(self.current_symbol))
        # return self.list_file[self.line_count]

    def get_number(self):
        number = ""
        if self.current_character.isdigit():
            number = self.current_character
        """while True:
            char = self.input_file.read(1)
            if char == '':
                break
            if char.isdigit():
                number = char
                break"""

        while True:

            nextchar = self.input_file.read(1)
            self.character_count += 1
            if nextchar.isdigit():
                number = number + nextchar
                continue
            else:
                self.current_character = nextchar
                break
        if len(number) == 0:
            return -1
        else:
            return int(number)

    def get_symbol(self):
        """Return the symbol type and ID of the next sequence of characters.

        If the current character is not recognised, both symbol type and ID
        are assigned None. Note: this function is called again (recursively)
        if it encounters a comment or end of line.
        """

        # print(self.get_line())
        """Return the symbol type and ID of the next sequence of characters."""

        # print(self.character_count)

        self.skip_spaces()

        # skipping over comments
        while self.current_character == '\\':
            if self.current_character == "\\":
                self.advance()
                if self.current_character == '*':
                    self.advance()
                    while self.current_character != '\\':
                        while self.current_character != '*':
                            if self.current_character == "\n":
                                self.line_count += 1
                                self.advance()
                            else:
                                self.advance()
                        self.advance()
                    self.advance()

                elif self.current_character == '\\':
                    while self.current_character != '\n':
                        self.advance()

                else:
                    return [None, None]

            self.skip_spaces()

        # current character now not whitespace
        if self.current_character.isalpha():  # name
            self.name_string = self.get_name()
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.name_string

            if self.name_string in self.keywords_list:
                symbol_type = self.KEYWORD
                symbol_id = self.names.query(self.name_string)

            else:

                symbol_type = self.NAME
                [symbol_id] = self.names.lookup([self.name_string])

        elif self.current_character.isdigit():  # number
            symbol_id = self.get_number()
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = str(symbol_id)
            symbol_type = self.NUMBER

        elif self.current_character == ",":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.COMMA
            symbol_id = None
            self.advance()

        elif self.current_character == ";":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.SEMICOLON
            symbol_id = None
            self.advance()

        elif self.current_character == ":":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.COLON
            symbol_id = None
            self.advance()

        elif self.current_character == ".":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.DOT
            symbol_id = None
            self.advance()

        elif self.current_character == '\n':
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.NEWLINE
            symbol_id = None
            self.advance()

        elif self.current_character == "":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.EOF
            symbol_id = None

        elif self.current_character == "-":
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            self.advance()
            if self.current_character == ">":
                self.two_prev_symbol = self.prev_symbol
                self.prev_symbol = self.current_symbol
                self.current_symbol = self.current_character
                symbol_type = self.ARROW
                symbol_id = None
                self.advance()
            else:
                self.two_prev_symbol = self.prev_symbol
                self.prev_symbol = self.current_symbol
                self.current_symbol = self.current_character
                symbol_type = None
                symbol_id = None
                self.advance()

        else:  # not a valid character
            self.two_prev_symbol = self.prev_symbol
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = None
            symbol_id = None
            self.advance()

        # self.skip_spaces()

        return [symbol_type, symbol_id]