"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.

Written by Ieva
"""

from errors import Errors


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

        [self.NO_DEVICE_KEYWORD, self.NO_CONNECTIONS_KEYWORD,
         self.NO_MONITOR_KEYWORD, self.MISSING_COLON, self.MISSING_SEMICOLON,
         self.INVALID_DEVICE_NAME, self.MISSING_DELIMITER, self.PORT_MISSING,
         self.INVALID_OUTPUT, self.INVALID_INPUT, self.MISSING_ARROW,
         self.NOT_ALL_INPUTS_CONNECTED, self.UNEXPECTED_SYMBOL,
         self.PREMATURE_EOF, self.COMMA_NOT_SEMICOLON,
         self.CONNECTIONS_DUPLICATE
         ] = self.names.unique_error_codes(16)

        self.device_list = ["DTYPE", "XOR", "AND", "NAND", "OR", "NOR",
                            "SWITCH", "CLOCK", "RC"]
        self.type_id_list = self.names.lookup(self.device_list)
        self.section_headers = [self.scanner.DEVICES_ID,
                                self.scanner.CONNECTIONS_ID,
                                self.scanner.MONITOR_ID]

        self.errors = Errors(devices, network, monitors, self)

        self.log = False
        self.count_errors = True  # Set to False once EOF is reached

    # Method for debugging purposes
    def _log(self, msg):
        if self.log:
            print(msg)

    def parse_network(self):
        """Parse the circuit definition file.

        Return: True if no errors detected, False otherwise.
        """
        no_error = True

        self._log("Start parsing")
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        no_error &= self._parse_section('device',
                                        self.scanner.DEVICES_ID,
                                        self.NO_DEVICE_KEYWORD)
        # Returns after a semicolon or the next keyword is detected
        # If keyword wasn't yet detected, it stopped on the semicolon. Hence,
        # read the next symbol which should be "CONNECTIONS"
        if not (self.symbol_type == self.scanner.KEYWORD and
                self.symbol_id == self.scanner.CONNECTIONS_ID):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If CONNNECTIONS: was written somewhere else in the file and after
        # error recovery there's
        # elif (self.symbol_type == self.scanner.KEYWORD and
        #       self.symbol_id == self.scanner.MONITORS_ID):
        #     no_error &= self._error(self.CONNECTIONS_DUPLICATE)
        no_error &= self._parse_section('connection',
                                        self.scanner.CONNECTIONS_ID,
                                        self.NO_CONNECTIONS_KEYWORD)
        # Returns after a semicolon, EOF or the next keyword is detected
        # Check if all inputs connected (method returns TRUE if connected)
        if not self.network.check_network():
            no_error &= self._error(self.NOT_ALL_INPUTS_CONNECTED)
        # If keyword wasn't yet detected, it stopped on the semicolon. Hence,
        # read the next symbol which should be "MONITORS"
        if not (self.symbol_type == self.scanner.KEYWORD and
                self.symbol_id == self.scanner.MONITOR_ID):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # If symbol is EOF - all good. That's allowed. If not, parse section
        if self.symbol_type != self.scanner.EOF:
            no_error &= self._parse_section('monitor',
                                            self.scanner.MONITOR_ID,
                                            self.NO_MONITOR_KEYWORD)
        # Returns after a semicolon or EOF was detected

        # Print total number of errors
        if not no_error:
            print(_("Total number of errors detected: {}")
                  .format(self.error_counter))
        return no_error

    def _parse_section(self, section, keyword_id, missing_keyword_error):
        """Parse section. Detect missing keyword or colon."""
        no_error = True
        # Get next keyword to skip until (in case of error and no semicolon)
        if keyword_id == self.scanner.DEVICES_ID:
            next_keyword = self.scanner.CONNECTIONS_ID
        elif keyword_id == self.scanner.CONNECTIONS_ID:
            next_keyword = self.scanner.MONITOR_ID
        else:
            next_keyword = self.scanner.EOF

        # First symbol must be the keyword of the section
        self._log("Parsing {} section".format(section))
        if (self.symbol_type == self.scanner.KEYWORD and
           self.symbol_id == keyword_id):
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            # Second symbol must be a colon
            if self.symbol_type == self.scanner.COLON:
                no_error &= self._parse_list(section, next_keyword)
                # Returns at semicolon/EOF or next keyword
                # Might return
            elif (self.symbol_type == self.scanner.KEYWORD or
                  self.symbol_type == self.scanner.NAME):
                # Report missing colon if next valid symbol type is read
                no_error &= self._error(self.MISSING_COLON,
                                        error_previous_symbol=True)
                self._skip_until(self.scanner.SEMICOLON, next_keyword)
            else:
                # Report "unexpected symbol" (e.g. ? instead of :)
                no_error &= self._error(self.MISSING_COLON)
                self._skip_until(self.scanner.SEMICOLON, next_keyword)
        else:
            no_error &= self._error(missing_keyword_error)
            self._skip_until(self.scanner.SEMICOLON, next_keyword)
        return no_error

    def _parse_list(self, section, next_keyword):
        """Parse the structure of the list: commas and semicolon.

        Also report missing semicolons and attempt error recovery.
        """
        self._log("Parse {} list".format(section))
        no_error = True
        # Method that will be called depending on section:
        method_name = '_parse_' + section
        parse_item = getattr(self, method_name)

        self._log("Before parsing item, symbol: {}, {}"
                  .format(self.symbol_type, self.symbol_id))
        no_error &= parse_item()
        # Parse_item returns successfully only when , or ; is detected
        # If an error has happened, skip until next comma or semicolon
        if not no_error:
            self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON,
                             next_keyword)

        self._log("After parsing item, symbol: {}, {}"
                  .format(self.symbol_type, self.symbol_id))
        # If a comma at the end of the item, keep reading items
        while self.symbol_type == self.scanner.COMMA:
            no_error &= parse_item()
            if self.symbol_type == self.scanner.COLON:
                # Deal with comma instead of semicolon error seperately
                self._skip_until(self.scanner.SEMICOLON)
                return no_error
            elif not no_error:
                self._skip_until(self.scanner.COMMA, self.scanner.SEMICOLON,
                                 next_keyword)
                self._log("After skip {}".format(self.symbol_type))

        # Semicolon is checked in section parsing

        return no_error

    # Some code in item parsing is repeated from Devices and Network classes
    # to allow better error location reporting.

    def _parse_device(self):
        """Parse device: device type, name and parameters."""
        self._log("Parse device")
        no_error = True
        device_type, device_id, device_param = None, None, None

        # Device type (saved as keywords)
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.KEYWORD:
            if self.symbol_id not in self.section_headers:
                device_type = self.symbol_id
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            elif self.symbol_id == self.scanner.CONNECTIONS_ID:
                # Check if next symbol is colon. If yes, a comma was placed
                # at the end of the list and not semicolon -> return.
                # The way errors are handeled, the CONNECTIONS section is
                # going to be skipped.
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
                if self.symbol_type == self.scanner.COLON:
                    no_error &= self._error(self.COMMA_NOT_SEMICOLON,
                                            no_marker=True)
                    return no_error
                else:
                    no_error &= self._error(self.devices.BAD_DEVICE,
                                            error_previous_symbol=True)
        else:
            no_error &= self._error(self.devices.BAD_DEVICE)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Device name (saved as name only if name is valid)
        if self.symbol_type == self.scanner.NAME:
            device_id = self.symbol_id
            # Check for duplicate device
            if self.devices.get_device(device_id) is not None:
                no_error &= self._error(self.devices.DEVICE_PRESENT)
        else:
            no_error &= self._error(self.INVALID_DEVICE_NAME)

        # Device parameters
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NUMBER:
            # Check if parameter is valid is done in Devices class
            device_param = self.symbol_id
            # Read one more to end up at the end of device definition
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        # Report an error if expected parameter is not a number
        elif (device_type in self.type_id_list and
              device_type != self.devices.D_TYPE and
              device_type != self.devices.XOR):
            no_error &= self._error(self.devices.INVALID_QUALIFIER)

        # Parse delimiter
        no_error &= self._parse_delimiter()

        # Make device
        if no_error:
            error_code = self.devices.make_device(device_id, device_type,
                                                  device_param)
            if error_code in [self.devices.INVALID_QUALIFIER,
                              self.devices.NO_QUALIFIER,
                              self.devices.QUALIFIER_PRESENT]:
                no_error &= self._error(error_code,
                                        error_previous_symbol=True)
            elif error_code != self.devices.NO_ERROR:
                # Most errors should have been caught before this.
                # If not, print the line without the marker as the error
                # location is not known at this point
                no_error &= self._error(error_code, no_marker=True)

        return no_error

    def _parse_connection(self):
        """Parse connection: devices and ports, arrow symbol."""
        self._log("Parse connection")
        no_error = True
        first_device_id, first_port_id = None, None
        second_device_id, second_port_id = None, None

        device = None
        # First device name
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NAME:
            first_device_id = self.symbol_id
            device = self.devices.get_device(first_device_id)
            if device is None:
                no_error &= self._error(self.network.DEVICE_ABSENT)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        elif (self.symbol_type == self.scanner.KEYWORD and
              self.symbol_id == self.scanner.MONITOR_ID):
            # Check if next symbol is colon. If yes, a comma was placed
            # at the end of the list and not semicolon -> return.
            # The way errors are handeled, the MONITOR section is
            # going to be skipped.
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
            if self.symbol_type == self.scanner.COLON:
                no_error &= self._error(self.COMMA_NOT_SEMICOLON,
                                        no_marker=True)
                return no_error
            else:
                no_error &= self._error(self.INVALID_DEVICE_NAME,
                                        error_previous_symbol=True)
        else:
            no_error &= self._error(self.INVALID_DEVICE_NAME)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        # Next might be the arrow or dot
        if self.symbol_type == self.scanner.DOT:
            no_dot_error, first_port_id = self._parse_dot_structure(
                                device, [self.scanner.ARROW], input=False)
            no_error &= no_dot_error
            # Returns where the arrow should be

        # Parse arrow and go to the name symbol
        if self.symbol_type == self.scanner.NAME:
            no_error &= self._error(self.MISSING_ARROW,
                                    error_previous_symbol=True)
        elif self.symbol_type == self.scanner.ARROW:
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        else:
            no_error &= self._error(self.MISSING_ARROW)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        device = None
        # Second device name
        if self.symbol_type == self.scanner.NAME:
            second_device_id = self.symbol_id
            device = self.devices.get_device(second_device_id)
            if device is None:
                no_error &= self._error(self.network.DEVICE_ABSENT)
        else:
            no_error &= self._error(self.INVALID_DEVICE_NAME)

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.DOT:
            no_dot_error, second_port_id = self._parse_dot_structure(
                                device,
                                [self.scanner.COMMA, self.scanner.SEMICOLON],
                                input=True)
            no_error &= no_dot_error
            # Returns after comma or semicolon is reached

        # Parse semicolon/comma
        no_error &= self._parse_delimiter()

        # Make connection
        if no_error:
            error_code = self.network.make_connection(
                                first_device_id, first_port_id,
                                second_device_id, second_port_id)
            if error_code != self.network.NO_ERROR:
                no_error &= self._error(error_code, no_marker=True)

        return no_error

    def _parse_monitor(self):
        """Parse monitor: devices and ports."""
        self._log("Parse monitor")
        no_error = True
        device_id, output_id = None, None

        device = None
        # Device name
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NAME:
            device_id = self.symbol_id
            device = self.devices.get_device(device_id)
            if device is None:
                no_error &= self._error(self.network.DEVICE_ABSENT)
        else:
            no_error &= self._error(self.INVALID_DEVICE_NAME)

        # Next might be comma/semicolon or dot
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.DOT:
            no_dot_error, output_id = self._parse_dot_structure(
                                device,
                                [self.scanner.COMMA, self.scanner.SEMICOLON],
                                input=False)
            no_error &= no_dot_error
            # Returns after comma or semicolon is reached

        # Parse semicolon/comma
        no_error &= self._parse_delimiter()

        # Make a monitor
        if no_error:
            error_code = self.monitors.make_monitor(device_id, output_id)
            if error_code == self.monitors.MONITOR_PRESENT:
                no_error &= self._error(error_code, error_previous_symbol=True)
            elif error_code != self.monitors.NO_ERROR:
                no_error &= self._error(error_code, no_marker=True)

        return no_error

    def _parse_delimiter(self):
        """Parse comma/semicolon at the end of an item description."""
        no_error = True

        if (self.symbol_type == self.scanner.NAME or
           self.symbol_type == self.scanner.KEYWORD):
            # Error location if it goes to the next valid symbol
            # (usually new line)
            no_error &= self._error(self.MISSING_DELIMITER,
                                    error_previous_symbol=True)
        elif (self.symbol_type != self.scanner.COMMA and
              self.symbol_type != self.scanner.SEMICOLON):
            # Error location if there's something unexpected (e.g. ?, not ;)
            no_error &= self._error(self.MISSING_DELIMITER)

        return no_error

    def _parse_dot_structure(self, device, list_expected_end_symbols, input):
        """Parse '<device_name>.<port_name> <expected_end_symbol>' stucture."""
        no_error = True
        port_id = None
        if input:
            port_error = self.INVALID_INPUT
            if device is not None:
                valid_ports = device.inputs
        else:
            port_error = self.INVALID_OUTPUT
            if device is not None:
                valid_ports = device.outputs

        # The function is entered if current symbol is dot. Next symbol should
        # be the name of the port
        [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        if self.symbol_type == self.scanner.NAME:
            port_id = self.symbol_id
            if (device is not None and port_id not in valid_ports):
                no_error &= self._error(port_error)
            # Read to possibly get the expected end symbol (-> or ,/;)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
        elif self.symbol_type in list_expected_end_symbols:
            # Example error: D1. -> A1.I1
            no_error &= self._error(self.PORT_MISSING,
                                    error_previous_symbol=True)
        else:
            # Something completely unexpected (e.g. D1.! -> A1.I1)
            no_error &= self._error(port_error)
            [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()

        return no_error, port_id

    def _error(self, error_code, error_previous_symbol=False, no_marker=False):
        """Count errors and print error message."""
        if self.count_errors:
            # If error is due to primature EOF, change count_errors flag
            # and thus stop reporting and counting errors after that
            if self.symbol_type == self.scanner.EOF:
                error_code = self.PREMATURE_EOF
                self.count_errors = False
            # Print error message (switched places for unit tests)
            print(self.errors.error_msg[error_code])
            # Some errors don't have/need specific location
            if (error_code != self.NOT_ALL_INPUTS_CONNECTED and
               error_code != self.PREMATURE_EOF and
               error_code != self.COMMA_NOT_SEMICOLON):
                self.scanner.get_line(error_previous_symbol, no_marker)
            # Update counter
            self.error_counter += 1

        return False

    def _skip_until(self, symb_type1, symb_type2=None, keyword_id=None):
        """Error recovery method.

        Stop parsing until one of the symbol types or a certain keyword is
        detected.
        """
        # Create symbol type list to avoid writing '==' checks
        skip_symb = [symb_type1, symb_type2, self.scanner.EOF]
        skip_symb = [symb for symb in skip_symb if symb is not None]
        # Check if current symbol is already the stopping one
        symb_found = self.symbol_type in skip_symb
        symb_found &= (self.symbol_id == keyword_id and
                       self.symbol_type == self.scanner.KEYWORD)
        while not symb_found:
            if (self.symbol_type in skip_symb or
                (self.symbol_type == self.scanner.KEYWORD and
                 self.symbol_id == keyword_id)):
                    symb_found = True
            else:
                [self.symbol_type, self.symbol_id] = self.scanner.get_symbol()
