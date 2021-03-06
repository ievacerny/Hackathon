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
        self.no_error = [devices.NO_ERROR, network.NO_ERROR, monitors.NO_ERROR,
                         parser.NO_ERROR]

        self.error_msg = {
            # Devices class
            devices.INVALID_QUALIFIER: "Error {}: Invalid parameter for the specified device."
                .format(devices.INVALID_QUALIFIER),
            devices.NO_QUALIFIER: "Error {}: Missing parameter for the specified device."
                .format(devices.NO_QUALIFIER),
            devices.BAD_DEVICE: "Error {}: Invalid device. Supported devices: SWITCH, CLOCK, AND, NAND, OR, NOR, XOR, DTYPE."
                .format(devices.BAD_DEVICE),
            devices.QUALIFIER_PRESENT: "Error {}: Specified devices doesn't need any parameters."
                .format(devices.QUALIFIER_PRESENT),
            devices.DEVICE_PRESENT: "Error {}: Device with such name already exists."
                .format(devices.DEVICE_PRESENT),
            # Network class
            network.INPUT_TO_INPUT: "Error {}: An input is connected to an input. Must be output -> input."
                .format(network.INPUT_TO_INPUT),
            network.OUTPUT_TO_OUTPUT: "Error {}: An output is connected to an output. Must be output -> input."
                .format(network.OUTPUT_TO_OUTPUT),
            network.INPUT_CONNECTED: "Error {}: Input is already connected."
                .format(network.INPUT_CONNECTED),
            network.PORT_ABSENT: "Error {}: Invalid input or output port."
                .format(network.PORT_ABSENT),
            network.DEVICE_ABSENT: "Error {}: Device has not been defined."
                .format(network.DEVICE_ABSENT),
            # Monitors class
            monitors.NOT_OUTPUT: "Error {}: Specified port is not an output. Only outputs can be monitored."
                .format(monitors.NOT_OUTPUT),
            monitors.MONITOR_PRESENT: "Error {}: Specified port is already being monitored."
                .format(monitors.MONITOR_PRESENT),
            # Parser class
            parser.NO_DEVICE_KEYWORD: "Error {}: Missing section header DEVICES."
                .format(parser.NO_DEVICE_KEYWORD),
            parser.NO_CONNECTIONS_KEYWORD: "Error {}: Missing section header CONNECTIONS."
                .format(parser.NO_CONNECTIONS_KEYWORD),
            parser.MISSING_COLON: "Error {}: Missing colon after the section header"
                .format(parser.MISSING_COLON),
            parser.MISSING_SEMICOLON: "Error {}: Missing semicolon at the end of the list."
                .format(parser.MISSING_SEMICOLON),
            parser.INVALID_DEVICE_NAME: "Error {}: Invalid device name. Name must start with a letter and must consist of letters and digits only. Name can't be the same as one of the device types."
                .format(parser.INVALID_DEVICE_NAME),
            parser.MISSING_DELIMITER: "Error {}: A comma between list items or a semicolon at the end of the list expected."
                .format(parser.MISSING_DELIMITER),
            parser.PORT_MISSING: "Error {}: After dot a valid input or output port should follow."
                .format(parser.PORT_MISSING),
            parser.INVALID_OUTPUT: "Error {}: The port is not an output. Must be output -> input."
                .format(parser.INVALID_OUTPUT),
            parser.INVALID_INPUT: "Error {}: The port is not an input. Must be output -> input."
                .format(parser.INVALID_OUTPUT),
            parser.MISSING_ARROW: "Error {}: Missing arrow in connection description."
                .format(parser.MISSING_ARROW),
            parser.NOT_ALL_INPUTS_CONNECTED: "Error {}: Not all inputs in the network are connected. Please check your circuit diagram."
                .format(parser.NOT_ALL_INPUTS_CONNECTED),
            parser.UNEXPECTED_SYMBOL: "Error {}: Unexpected symbol detected."
                .format(parser.UNEXPECTED_SYMBOL),
            parser.PREMATURE_EOF: "Error {}: File ended abruptly."
                .format(parser.PREMATURE_EOF)
        }
