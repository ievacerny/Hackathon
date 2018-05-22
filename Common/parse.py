"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.

Written by Ieva
"""


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.

    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.scanner = scanner
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.symbol_type = None
        self.symbol_id = None
        self.error_counter = 0

        [self.NO_ERROR, self.NOT_VALID_SYMBOL, self.NO_DEVICE_LIST_KEYWORD,
         self.MISSING_COLON, self.INVALID_DEVICE, self.DUPLICATE_NAME,
         self.INVALID_DEVICE_NAME, self.MORE_PARAMETERS_NEEDED,
         ] = self.names.unique_error_codes(6)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        no_errors = True

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == self.scanner.DEVICES_ID):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.COLON:
                self._parse_device_list()
            else:
                self._error(self.MISSING_COLON)
                self._skip_until(self.scanner.SEMICOLON)
                # TODO add skip to "CONNECTIONS"
        else:
            self.error(self.NO_DEVICE_LIST_KEYWORD)
            self._skip_until(self.scanner.SEMICOLON)
            # TODO add skip to "CONNECTIONS"

        # TODO check if skipped until CONNECTIONS
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == self.scanner.CONNECTIONS_ID):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.COLON:
                self._parse_connections_list()
            else:
                self._error(self.MISSING_COLON)
                self._skip_until(self.scanner.SEMICOLON)
                # TODO add skip to "MONITORS"
        else:
            self.error(self.NO_CONNECTIONS_LIST_KEYWORD)
            self._skip_until(self.scanner.SEMICOLON)
            # TODO add skip to "MONITORS"

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == self.scanner.MONITORS_ID):
            self._parse_monitors_list()

        return no_errors

    def _parse_device_list(self):
        # _parse_device returns when a comma, a semicolon is detected
        # or it returns with an error code
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        exit_code = self._parse_device()
        if exit_code != self.NO_ERROR:
            self._error(exit_code)
            self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
            # TODO add skip to "CONNECTIONS"
        while self.symbol_type == self.scanner.COMMA:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            exit_code = self._parse_device()
            if exit_code != self.NO_ERROR:
                self._error(exit_code)
                self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
                # TODO add skip to "CONNECTIONS"
        if self.symbol_type == self.scanner.SEMICOLON:
            return

    def _parse_connections_list(self):
        # _parse_device returns when a comma, a semicolon is detected
        # or it returns with an error code
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        exit_code = self._parse_connection()
        if exit_code != self.NO_ERROR:
            self._error(exit_code)
            self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
            # TODO add skip to "CONNECTIONS"
        while self.symbol_type == self.scanner.COMMA:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            exit_code = self._parse_connection()
            if exit_code != self.NO_ERROR:
                self._error(exit_code)
                self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
                # TODO add skip to "CONNECTIONS"
        if self.symbol_type == self.scanner.SEMICOLON:
            return

    def _parse_monitors_list(self):
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        exit_code = self._parse_monitor()
        if exit_code != self.NO_ERROR:
            self._error(exit_code)
            self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
            # TODO add skip to EOF
        while self.symbol_type == self.scanner.COMMA:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            exit_code = self._parse_monitor()
            if exit_code != self.NO_ERROR:
                self._error(exit_code)
                self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
                # TODO add skip to EOF
        if self.symbol_type == self.scanner.SEMICOLON:
            return

    def _parse_device(self):
        exit_code = self.NO_ERROR

        # Device types are keywords
        if self.symbol_type == self.scanner.KEYWORD:
            if self.symbol_id == self.names.query("SWITCH"):
                device_type = "SWITCH"
            elif self.symbol_id == self.names.query("CLOCK"):
                device_type = "CLOCK"
            elif (self.symbol_id in self.names.lookup(["DTYPE", "XOR"])):
                device_type = "DTYPE/XOR"
            elif (self.symbol_id in self.names.lookup(["AND", "NAND",
                                                      "OR", "NOR"])):
                device_type = "AND/NAND/OR/NOR"
            else:
                exit_code = self.INVALID_DEVICE
        else:
            exit_code = self.INVALID_DEVICE

        # Quit if error
        if exit_code != self.NO_ERROR:
            return exit_code

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # Check if device name valid
        if self.symbol_type == self.scanner.NAME:
            # If index of the name is the last one in the name_table, it's a
            # new name. If not, it has been declared before -> duplicate
            last_index = len(self.names.name_table)-1
            if self.symbol_id != last_index:
                exit_code = self.DUPLICATE_NAME
        else:
            exit_code = self.INVALID_DEVICE_NAME

        # Quit if error
        if exit_code != self.NO_ERROR:
            return exit_code

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # Check if extra parameters needed
        if (self.symbol_type == self.scanner.COMMA or
           self.symbol_type == self.scanner.SEMICOLON):
            if device_type == "DTYPE/XOR":
                return exit_code  # No further parameters expected, device done
            else:
                exit_code = self.MORE_PARAMETERS_NEEDED
        elif self.symbol_type == self.scanner.NUMBER:
            if device_type == "DTYPE/XOR":
                exit_code = self.NO_MORE_PARAMETERS_NEEDED
            elif self.symbol_id < 0:
                exit_code = self.NEGATIVE_PARAMETER
            elif self.symbol_id == 0:
                if device_type == "CLOCK":
                    exit_code = self.CLOCK_0_CYCLE
                elif device_type == "AND/NAND/OR/NOR":
                    exit_code = self.DEVICE_0_INPUTS
            elif self.symbol_id > 1 and device_type == "SWITCH":
                exit_code = self.NONBINARY_SWITCH_STATE
            elif self.symbol_id > 16 and device_type == "AND/NAND/OR/NOR":
                exit_code = self.MORE_THAN_16_INPUTS
        else:
            if device_type == "DTYPE/XOR":
                exit_code = self.EXPECTED_DELIMITER
            else:
                exit_code = self.PARAMETER_NOT_NUMBER

        # Quit if error
        if exit_code != self.NO_ERROR:
            return exit_code

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # Check if comma or semicolon
        if (self.symbol_type != self.scanner.COMMA and
           self.symbol_type != self.scanner.SEMICOLON):
            exit_code = self.EXPECTED_DELIMITER

        return exit_code

    def _parse_connection(self):
        exit_code = self.NO_ERROR

        # Device name
        if self.symbol_type != self.scanner.NAME:
            exit_code = self.INVALID_DEVICE_NAME
            return exit_code

        # Checks if valid device and if valid port done through network
        first_device_id = self.symbol_id
        first_port_id = None

        # Next might be the arrow or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.ARROW:
            pass
        elif self.symbol_type == self.scanner.DOT:
            # Get output name
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type != self.scanner.NAME:
                exit_code = self.INVALID_PORT_NAME
                return exit_code
            first_port_id = self.symbol_id
            # Get arrow
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type != self.scanner.ARROW:
                exit_code = self.EXPECTEED_ARROW
                return exit_code
        else:
            exit_code = self.UNEXPECTED_SYMBOL

        # Next should be output
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type != self.scanner.NAME:
            exit_code = self.INVALID_DEVICE_NAME
            return exit_code

        # Checks if valid device and if valid port done through network
        second_device_id = self.symbol_id
        second_port_id = None

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.DOT:
            # Get input name
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type != self.scanner.NAME:
                exit_code = self.INVALID_PORT_NAME
                return exit_code
            second_port_id = self.symbol_id

        if (self.symbol_type != self.scanner.COMMA and
           self.symbol_type != self.scanner.SEMICOLON):
            exit_code = self.UNEXPECTED_SYMBOL

        return exit_code

    def _parse_monitor(self):
        exit_code = self.NO_ERROR

        # Device name
        if self.symbol_type != self.scanner.NAME:
            exit_code = self.INVALID_DEVICE_NAME
            return exit_code

        device_id = self.symbol_id

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.DOT:
            # Get input name
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type != self.scanner.NAME:
                exit_code = self.INVALID_PORT_NAME
                return exit_code
            port_id = self.symbol_id

        if (self.symbol_type != self.scanner.COMMA and
           self.symbol_type != self.scanner.SEMICOLON):
            exit_code = self.UNEXPECTED_SYMBOL

        # TODO check if device_id and port_id are valid

        return exit_code

    def _error(self, error_code):
        self.error_counter += 1
        # FIXME change error detection so that the cursor is on the right line
        # TODO how to deal with device split in multiple lines?

        self.scanner.print_line(error_code)
        # TODO think about the best way to store and print error messages

    def _skip_until(self, symb1, symb2=None, symb3=None):
        skip_symb = [symb1, symb2, symb3]
        skip_symb = [symb for symb in skip_symb if symb is not None]

        symb_not_found = True
        while symb_not_found:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if (self.symbol_type in skip_symb or
               self.symbol_type == self.scanner.EOF):
                symb_not_found = False
