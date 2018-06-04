"""Save the error codes and messages for use in scripts and modules.

Imported into Parser that uses it to print error messages.

Written by Ieva
"""


class Errors:
    """Save all errors codes and errors messages for error reporting.

    Parameters
    ----------
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    parser: instance of the parse.Parser() class.

    """

    def __init__(self, devices, network, monitors, parser):
        """Initialise error messages attribute and collects all errors."""
        
        self.no_error = [devices.NO_ERROR, network.NO_ERROR, monitors.NO_ERROR]

        self.error_msg = {
            # Devices class
            devices.INVALID_QUALIFIER: _("Error {}: Invalid parameter for the specified device.")
                .format(devices.INVALID_QUALIFIER),
            devices.NO_QUALIFIER:_("Error {}: Missing parameter for the specified device.")
                .format(devices.NO_QUALIFIER),
            devices.BAD_DEVICE:_("Error {}: Invalid device. Supported devices: SWITCH, CLOCK, AND, NAND, OR, NOR, XOR, DTYPE, RC.")
                .format(devices.BAD_DEVICE),
            devices.QUALIFIER_PRESENT:_("Error {}: Specified devices does not need any parameters.")
                .format(devices.QUALIFIER_PRESENT),
            devices.DEVICE_PRESENT:_("Error {}: Device with such name already exists.")
                .format(devices.DEVICE_PRESENT),
            # Network class
            network.INPUT_TO_INPUT:_("Error {}: An input is connected to an input. Must be output -> input.")
                .format(network.INPUT_TO_INPUT),
            network.OUTPUT_TO_OUTPUT:_("Error {}: An output is connected to an output. Must be output -> input.")
                .format(network.OUTPUT_TO_OUTPUT),
            network.INPUT_CONNECTED:_("Error {}: Specified input is already connected.")
                .format(network.INPUT_CONNECTED),
            network.PORT_ABSENT:_("Error {}: Invalid input or output port.")
                .format(network.PORT_ABSENT),
            network.DEVICE_ABSENT:_("Error {}: Device has not been defined.")
                .format(network.DEVICE_ABSENT),
            # Monitors class
            monitors.NOT_OUTPUT:_("Error {}: Specified port is not an output. Only outputs can be monitored.")
                .format(monitors.NOT_OUTPUT),
            monitors.MONITOR_PRESENT:_("Error {}: Specified port is already being monitored.")
                .format(monitors.MONITOR_PRESENT),
            # Parser class
            parser.NO_DEVICE_KEYWORD:_("Error {}: Expected section header 'DEVICES'.")
                .format(parser.NO_DEVICE_KEYWORD),
            parser.NO_CONNECTIONS_KEYWORD:_("Error {}: Expected section header 'CONNECTIONS'.")
                .format(parser.NO_CONNECTIONS_KEYWORD),
            parser.NO_MONITOR_KEYWORD:_("Error {}: There is no section header MONITOR, but a third section after the semicolon is found on file. Either semicolon is not placed correctly or section header is missing.")
                .format(parser.NO_MONITOR_KEYWORD),
            parser.MISSING_COLON:_("Error {}: Expected a colon after the section header.")
                .format(parser.MISSING_COLON),
            parser.MISSING_SEMICOLON:_("Error {}: Expected a semicolon at the end of the list.")
                .format(parser.MISSING_SEMICOLON),
            parser.INVALID_DEVICE_NAME:_("Error {}: Invalid device name. Name must start with a letter and must consist of letters and digits only. Name can't be the same as one of the device types.")
                .format(parser.INVALID_DEVICE_NAME),
            parser.MISSING_DELIMITER:_("Error {}: A comma between list items or a semicolon at the end of the list expected.")
                .format(parser.MISSING_DELIMITER),
            parser.PORT_MISSING:_("Error {}: After dot a valid input or output port should follow.")
                .format(parser.PORT_MISSING),
            parser.INVALID_OUTPUT:_("Error {}: Port must be a valid output of the specified device.")
                .format(parser.INVALID_OUTPUT),
            parser.INVALID_INPUT:_("Error {}: Port must be a valid input of the specified device.")
                .format(parser.INVALID_OUTPUT),
            parser.MISSING_ARROW:_("Error {}: Missing arrow in the connection description.")
                .format(parser.MISSING_ARROW),
            parser.NOT_ALL_INPUTS_CONNECTED:_("Error {}: Not all inputs in the network are connected. Please check your circuit diagram.")
                .format(parser.NOT_ALL_INPUTS_CONNECTED),
            parser.UNEXPECTED_SYMBOL:_("Error {}: Unexpected symbol detected.")
                .format(parser.UNEXPECTED_SYMBOL),
            parser.PREMATURE_EOF:_("Error {}: File ended abruptly.")
                .format(parser.PREMATURE_EOF),
            parser.COMMA_NOT_SEMICOLON:_("Error {}: A comma was found instead of a semicolon at the end of the list. Or a section header is missplaced. Please check the definition file.")
                .format(parser.COMMA_NOT_SEMICOLON)
        }
