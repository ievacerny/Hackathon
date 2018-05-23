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

        [self.NO_ERROR, self.NO_DEVICE_KEYWORD, self.NO_CONNECTIONS_KEYWORD,
         self.MISSING_COLON, self.MISSING_SEMICOLON, self.BAD_DEVICE,
         self.INVALID_DEVICE_NAME, self.MISSING_DELIMITER,
         self.UNDEFINED_DEVICE, self.PORT_ABSENT, self.PORT_MISSING,
         self.MISSING_ARROW, self.DUPLICATE_NAME,
         self.MORE_PARAMETERS_NEEDED, self.UNEXPECTED_SYMBOL
         ] = range(15)
        # = self.names.unique_error_codes(11)

        self.device_list = ["DTYPE", "XOR", "AND", "NAND", "OR", "NOR",
                            "SWITCH", "CLOCK"]

        self.log = True

    # Temporary method for error printing
    def _log(self, msg):
        if self.log:
            print(msg)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        no_errors = True

        self._log("Start parsing")
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        self._log("Device section symbol info: {}, {}".format(self.symbol_type, self.symbol_id))
        if self.symbol_type == 5 or self.symbol_type == 3:
            self._log(self.names.get_name_string(self.symbol_id))
        no_errors = self._parse_section('device',
                                        self.scanner.DEVICES_ID,
                                        self.NO_DEVICE_KEYWORD)
        # Currently returns after a semicolon was detected

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        self._log("Connections section symbol info: {}, {}".format(self.symbol_type, self.symbol_id))
        if self.symbol_type == 5 or self.symbol_type == 3:
            self._log(self.names.get_name_string(self.symbol_id))
        no_errors = self._parse_section('connection',
                                        self.scanner.CONNECTIONS_ID,
                                        self.NO_CONNECTIONS_KEYWORD)
        # Currently returns after a semicolon was detected

        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        self._log("Monitors section symbol info: {}, {}".format(self.symbol_type, self.symbol_id))
        if self.symbol_type == 5 or self.symbol_type == 3:
            self._log(self.names.get_name_string(self.symbol_id))
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == self.scanner.MONITOR_ID):
            no_errors = self._parse_section('monitor',
                                            self.scanner.MONITOR_ID, 0)
        # Currently returns after a semicolon was detected

        return no_errors

    def _parse_section(self, section, keyword_id, missing_keyword_error):
        """Parse section keyword and colon."""
        no_errors = True
        # First symbol must be the keyword of the section
        self._log("Parsing {} section".format(section))
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == keyword_id):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            # Second symbol must be a colon
            if self.symbol_type == self.scanner.COLON:
                # Parse the list. Returns after the list is parsed or a
                # semicolon is reached (or EOF)
                no_errors = self._parse_list(section)
            else:
                no_errors = self._error(self.MISSING_COLON)
                self._log("ERROR: Missing colon")
                self._skip_until(self.scanner.SEMICOLON)
                # TODO add skip to next section keyword
        else:
            no_errors = self._error(missing_keyword_error)
            self._log("ERROR: Missing keyword")
            self._skip_until(self.scanner.SEMICOLON)
            # TODO add skip to next section keyword
        return no_errors

    def _parse_list(self, section):
        """Parse the structure of the list: commas and semicolon."""
        self._log("Parse {} list".format(section))
        no_errors = True
        # Method that will be called depending on section:
        method_name = '_parse_' + section
        parse_item = getattr(self, method_name)

        self._log("Before parsing item, symbol: {}, {}".format(self.symbol_type, self.symbol_id))
        no_errors = parse_item()
        # Parse_item returns successfully only when , or ; is detected
        # If an error has happened, skip until next comma or semicolon
        if not no_errors:
            # self._error(exit_code)  # TODO move inside parse_item()
            self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
            # TODO add skip to next section keyword

        self._log("After parsing item, symbol: {}, {}".format(self.symbol_type, self.symbol_id))
        # If a comma at the end of the item, keep reading items
        while self.symbol_type == self.scanner.COMMA:
            no_errors = parse_item()
            if not no_errors:
                # self._error(exit_code)  # TODO move inside parse_item()
                self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON)
                # TODO add skip to next section keyword

        # At this point, symbol posibilities: ;/EOF/(section keyword)
        if self.symbol_type != self.scanner.SEMICOLON:
            no_errors = self._error(self.MISSING_SEMICOLON)
            self._log("ERROR: Missing semicolon")

        return no_errors

    def _parse_device(self):
        """Parse device: device type, name and parameters."""
        self._log("Parse device")
        no_errors = True
        device_type = None
        device_id = None
        device_param = None

        # First symbol should be device type (saved as keywords)
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If device supported is checked in Devices class
        if self.symbol_type == self.scanner.KEYWORD:
            device_type = self.symbol_id
        else:
            no_errors = self._error(self.BAD_DEVICE)
            self._log("ERROR: Invalid device: {}".format(self.symbol_type))

        # Device name
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NAME:
            # Type name is given only if name satisfies character requirements
            # If device has already been added is checked in Devices class
            device_id = self.symbol_id
        else:
            no_errors = self._error(self.INVALID_DEVICE_NAME)
            self._log("ERROR: Invalid device name")

        # Device parameters
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NUMBER:
            # If parameters is valid is checked in Devices class
            device_param = self.symbol_id
            # Read one more to end up at the end of legit device definition
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        if self.symbol_type == self.scanner.KEYWORD:
            no_errors = self._error(self.MISSING_DELIMITER)
            self._log("ERROR: Missing delimiter")
        elif (self.symbol_type != self.scanner.COMMA and
              self.symbol_type != self.scanner.SEMICOLON):
            no_errors = self._error(self.UNEXPECTED_SYMBOL)
            self._log("ERROR: Unexpected symbol")

        if no_errors:
            error_code = self.devices.make_device(device_id, device_type,
                                                  device_param)
            if error_code != self.NO_ERROR:
                no_errors = self._error(error_code)
                self._log("ERROR: Devices error {}".format(error_code))

        return no_errors

    def _parse_connection(self):
        """Parse connection: devices and ports, arrow symbol."""
        self._log("Parse connection")
        no_errors = True
        first_device_id = None
        first_port_id = None
        second_device_id = None
        second_port_id = None

        # First symbol should be a device name
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NAME:
            first_device_id = self.symbol_id
        else:
            no_errors = self._error(self.INVALID_DEVICE_NAME)
            self._log("ERROR: Invalid device name: {}".format(self.symbol_type))

        # Next might be the arrow or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If dot, read until arrow placement is reached
        if self.symbol_type == self.scanner.DOT:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.NAME:
                first_port_id = self.symbol_id
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            elif self.symbol_type == self.scanner.ARROW:
                no_errors = self._error(self.PORT_MISSING)
                self._log("ERROR: Port missing: {}".format(self.symbol_type))
            else:
                no_errors = self._error(self.PORT_ABSENT)
                self._log("ERROR: Invalid port: {}".format(self.symbol_type))
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Parse arrow and go to the name symbol
        if self.symbol_type == self.scanner.NAME:
            no_errors = self._error(self.MISSING_ARROW)
            self._log("ERROR: Missing arrow")
        elif self.symbol_type == self.scanner.ARROW:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        else:
            no_errors = self._error(self.UNEXPECTED_SYMBOL)
            self._log("ERROR: Unexpected symbol instead of arrow")
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Parse device name
        if self.symbol_type == self.scanner.NAME:
            second_device_id = self.symbol_id
        else:
            no_errors = self._error(self.INVALID_DEVICE_NAME)
            self._log("ERROR: Invalid device name: {}".format(self.symbol_type))

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If dot, read until comma.semicolon placement is reached
        if self.symbol_type == self.scanner.DOT:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.NAME:
                second_port_id = self.symbol_id
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            elif (self.symbol_type == self.scanner.COMMA or
                  self.symbol_type == self.scanner.SEMICOLON):
                no_errors = self._error(self.PORT_MISSING)
                self._log("ERROR: Port missing: {}".format(self.symbol_type))
            else:
                no_errors = self._error(self.PORT_ABSENT)
                self._log("ERROR: Invalid port: {}".format(self.symbol_type))
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Parse semicolon/comma
        if(self.symbol_type == self.scanner.NAME or
           self.symbol_type == self.scanner.KEYWORD):
            no_errors = self._error(self.MISSING_DELIMITER)
            self._log("ERROR: Missing delimiter")
        elif(self.symbol_type != self.scanner.COMMA and
             self.symbol_type != self.scanner.SEMICOLON):
            no_errors = self._error(self.UNEXPECTED_SYMBOL)
            self._log("ERROR: Unexpected symbol instead of comma/semicolon")

        if no_errors:
            error_code = self.network.make_connection(
                                first_device_id, first_port_id,
                                second_device_id, second_port_id)
            if error_code != self.NO_ERROR:
                no_errors = self._error(error_code)
                self._log("ERROR: Network error {}".format(error_code))

        return no_errors

    def _parse_monitor(self):
        """Parse monitor: devices and ports."""
        self._log("Parse monitor")
        no_errors = True
        device_id = None
        output_id = None

        # First symbol should be name
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # Device name
        if self.symbol_type == self.scanner.NAME:
            device_id = self.symbol_id
        else:
            no_errors = self._error(self.INVALID_DEVICE_NAME)
            self._log("ERROR: Invalid device name")

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If dot, read until comma.semicolon placement is reached
        if self.symbol_type == self.scanner.DOT:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.NAME:
                output_id = self.symbol_id
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            elif (self.symbol_type == self.scanner.COMMA or
                  self.symbol_type == self.scanner.SEMICOLON):
                no_errors = self._error(self.PORT_MISSING)
                self._log("ERROR: Port missing: {}".format(self.symbol_type))
            else:
                no_errors = self._error(self.PORT_ABSENT)
                self._log("ERROR: Invalid port: {}".format(self.symbol_type))
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Parse semicolon/comma
        if self.symbol_type == self.scanner.NAME:
            no_errors = self._error(self.MISSING_DELIMITER)
            self._log("ERROR: Missing delimiter")
        elif(self.symbol_type != self.scanner.COMMA and
             self.symbol_type != self.scanner.SEMICOLON):
            no_errors = self._error(self.UNEXPECTED_SYMBOL)
            self._log("ERROR: Unexpected symbol instead of comma/semicolon")

        if no_errors:
            error_code = self.monitors.make_monitor(device_id, output_id)
            if error_code != self.NO_ERROR:
                no_errors = self._error(error_code)
                self._log("ERROR: Monitor error {}".format(error_code))

        return no_errors

    def _error(self, error_code):
        """Count errors and print error message."""
        # TODO create a separate flag once proper error reporting is done
        # Stop counting errors after EOF error is detected once
        if self._log:
            self.error_counter += 1
            # self.scanner.print_line(error_code)

        if self.symbol_type == self.scanner.EOF:
            self._log("ERROR: File ends abruptly.")
            # If end of file, stop detecting and counting errors
            self._log = False

        # TODO think about the best way to store and print error messages
        # TODO return True/False depending if an error was detected
        return True

    def _skip_until(self, symb1, symb2=None, symb3=None):
        """Stop parsing until one of the symbols is detected."""
        # TODO improve the code
        skip_symb = [symb1, symb2, symb3]
        skip_symb = [symb for symb in skip_symb if symb is not None]

        symb_not_found = True
        while symb_not_found:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if (self.symbol_type in skip_symb or
               self.symbol_type == self.scanner.EOF):
                symb_not_found = False
