"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
"""

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
            self.input_file = open(path, 'r')
        except (FileNotFoundError, IsADirectoryError):
            print("Error: Filename incorrect or file doesn't exist.")
            sys.exit()

        self.list_file = [line.rstrip('\n') for line in open(path, 'r')]

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.COLON,
                                 self.KEYWORD, self.NUMBER, self.NAME, self.ARROW,
                                 self.EOF, self.NEWLINE, self.DOT] = range(10)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR", "DTYPE", "XOR", "AND", "NAND", "OR", "NOR", "SWITCH",
                              "CLOCK", "RC", "NOT"]
        self.names.lookup(self.keywords_list)
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list[:3])
        self.current_character = ""
        self.name_string = ''
        self.character_count = -1
        self.line_count = 0
        self.current_symbol = ''
        self.prev_symbol = ''
        self.space_count = 0
        self.comment_lines = []
        self.advance()
        self.skip_spaces()

    def advance(self):
        """reads one further character into the document"""

        char = self.input_file.read(1)
        self.character_count += 1
        self.current_character = char
        return char

    def skip_spaces(self):
        """"advances until the character is no longer a space"""

        while self.current_character.isspace():

            if self.current_character == "\n":
                self.character_count = -1
                self.line_count += 1

            self.space_count += 1
            self.current_character = self.input_file.read(1)
            self.character_count += 1

    def get_name(self):
        """If the current character is a letter, advances until the current character isn't a letter or a number and
        returns the name"""

        name = ''
        if self.current_character.isalpha():
            name = self.current_character

            while True:
                nextchar = self.input_file.read(1)
                self.character_count += 1
                if nextchar.isalnum():
                    name = name + nextchar
                    continue
                else:
                    self.current_character = nextchar
                    break

        return name

    def cur_sym(self): # for testing
        """Prints current symbol."""

        print(self.current_symbol)

    def add_ignore(self):
        """lines to ignore when calling get_line and printing the previous line as they have comments"""

        line_index = self.line_count

        # The whole line is commented as only \* occurs at the beginning
        if ((self.list_file[line_index]).strip()).find('\\*') == 0 \
                and ((self.list_file[line_index]).strip()).find('*\\') == -1:
            self.comment_lines.append(line_index)

        # \* at the beginning of the line and *\ at the end of the line
        elif ((self.list_file[line_index]).strip()).find('*\\') == len(((self.list_file[line_index]).strip()))-2 \
                and ((self.list_file[line_index]).strip()).find('\\*') == 0:
            self.comment_lines.append(line_index)

        # The whole line is commented as only *\ occurs at the end
        elif ((self.list_file[line_index]).strip()).find('*\\') == len(((self.list_file[line_index]).strip()))-2 \
                and ((self.list_file[line_index]).strip()).find('\\*') == -1:
            self.comment_lines.append(line_index)

        # The whole line is commented as the line is between \* and *\ but neither occur in the line
        elif ((self.list_file[line_index]).strip()).find('\\*') == -1 \
                and ((self.list_file[line_index]).strip()).find('*\\') == -1:
            self.comment_lines.append(line_index)

    def get_line(self, before, arrow):
        """Called by the parser to print a line when an error occurs. If before is true, there is an issue with the
        previous symbol, if false, the current symbol, if arrow is true, the caret line doesn't need to be
        printed."""

        if before is True and arrow is False:
            symbol = self.current_symbol
            line = self.list_file[self.line_count]
            prev_line_index = self.line_count - 1
            character_no = self.character_count

            # uses character count to find the last symbol while disregarding comments and spaces
            while self.list_file[prev_line_index].isspace() is True or len(self.list_file[prev_line_index]) == 0 \
                    or ((self.list_file[prev_line_index]).strip()).find('\\\\') == 0 \
                    or prev_line_index in self.comment_lines:
                prev_line_index -= 1

            # if current symbol is the first on the line, then the previous symbol is the last on the previous line
            prev_line = self.list_file[prev_line_index]

            find_comment_end = (line.strip()).find('*\\') + 2
            line_cut = line[find_comment_end:]
            no_ws_cut = line_cut.strip()

            # find the last symbol while ignoring comments
            if ((line.strip()).find(symbol) == 0 or
                ((line.strip()).find('*\\') != -1 and no_ws_cut.find(symbol) == 0
                 and (line.strip()).find('\\*') == -1)
                or ((line.strip()).find('*\\') != -1 and line.strip().find('*\\') + 2 == (line.strip()).find(symbol)
                    and (line.strip()).find('\\*') == 0)):

                str_index = str(prev_line_index+1)
                len_index = len(str_index)
                print('Line ' + str_index + ': ' + prev_line)

                if prev_line.find('\\*') != -1:
                    arrow_index = prev_line.find('\\*') - 1

                elif prev_line.find('\\\\') != -1:
                    arrow_index = prev_line.find('\\\\') - 1

                else:
                    arrow_index = len(prev_line) - 1

                cut_line = prev_line[:arrow_index]
                arrow_line = ''
                for char in cut_line:
                    if not char.isspace():
                        arrow_line = arrow_line + ' '
                    else:
                        arrow_line = arrow_line + char

                print(' ' * (7+len_index) + arrow_line + '^')

            else:
                cur_index = self.line_count
                str_index = str(cur_index + 1)
                len_index = len(str_index)
                print('Line ' + str_index + ': ' + line)

                cut_line = line[:character_no - len(symbol) - 1 - self.space_count]
                arrow_line = ''
                for char in cut_line:
                    if not char.isspace():
                        arrow_line = arrow_line + ' '
                    else:
                        arrow_line = arrow_line + char

                print(' ' * (7 + len_index) + arrow_line + '^')

        elif before is False and arrow is True:
            # Just prints the line without a caret

            line = self.list_file[self.line_count]
            cur_index = self.line_count
            str_index = str(cur_index + 1)

            print('Line ' + str_index + ': ' + line)

        elif before is False and arrow is False:
            # Prints the current line with a caret beneath the current symbol
            
            line = self.list_file[self.line_count]
            cur_index = self.line_count
            str_index = str(cur_index + 1)
            len_index = len(str_index)
            character_no = self.character_count

            print('Line ' + str_index + ': ' + line)

            cut_line = line[:character_no - 1]
            arrow_line = ''

            for char in cut_line:

                if not char.isspace():
                    arrow_line = arrow_line + ' '
                else:
                    arrow_line = arrow_line + char

            print(' ' * (7 + len_index) + arrow_line + '^')

    def get_number(self):

        """When the current symbol is a number, advances until the end of the number and returns the number
        as an integer"""

        number = ""
        if self.current_character.isdigit():
            number = self.current_character

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

        """Return the symbol type and ID of the next sequence of characters."""

        self.space_count = 0

        self.skip_spaces()

        while self.current_character == '\\':  # skipping over spaces
            if self.current_character == "\\":
                self.advance()

                if self.current_character == '*':   # multi-line comment (between \* and *\)
                    self.add_ignore()
                    self.advance()
                    self.space_count += 2

                    # stops when it finds the symbol corresponding the end of comment or at end of file
                    while self.current_character != '\\' and self.current_character != '':

                        while self.current_character != '*' and self.current_character != '':

                            if self.current_character == "\n":
                                self.add_ignore()
                                self.line_count += 1
                                self.space_count = 0
                                self.character_count = -1
                                self.advance()

                            else:
                                self.advance()
                                self.space_count += 1

                        self.advance()
                        self.space_count += 1

                    self.advance()
                    self.space_count += 1

                elif self.current_character == '\\':    # single line comment (\\)
                    while self.current_character != '\n':
                        self.advance()
                else:   # there is only one slash meaning this isn't a recognised symbol
                    self.prev_symbol = self.current_symbol
                    self.current_symbol = "\\"
                    return [None, None]

            self.skip_spaces()

        if self.current_character.isalpha():  # name
            self.name_string = self.get_name()
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
            self.prev_symbol = self.current_symbol
            self.current_symbol = str(symbol_id)
            symbol_type = self.NUMBER

        elif self.current_character == ",":  # comma
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.COMMA
            symbol_id = None
            self.advance()

        elif self.current_character == ";":  # semi-colon
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.SEMICOLON
            symbol_id = None
            self.advance()

        elif self.current_character == ":":  # colon
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.COLON
            symbol_id = None
            self.advance()

        elif self.current_character == ".":  # dot
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.DOT
            symbol_id = None
            self.advance()

        elif self.current_character == '\n':  # new line
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.NEWLINE
            symbol_id = None
            self.advance()

        elif self.current_character == "":  # end of file
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = self.EOF
            symbol_id = None

        elif self.current_character == "-":  # detecting first character of arrow
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            self.advance()
            if self.current_character == ">":  # completing arrow
                self.prev_symbol = self.current_symbol
                self.current_symbol = self.current_character
                symbol_type = self.ARROW
                symbol_id = None
                self.advance()
            else:   # only - was detected which isn't valid
                self.prev_symbol = self.current_symbol
                self.current_symbol = self.current_character
                symbol_type = None
                symbol_id = None
                self.advance()

        else:  # not a valid character
            self.prev_symbol = self.current_symbol
            self.current_symbol = self.current_character
            symbol_type = None
            symbol_id = None
            self.advance()

        return [symbol_type, symbol_id]
