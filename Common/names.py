"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.name_counter = 0
        self.name_table_size = 1000
        self.name_table = [None] * self.name_table_size

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        index = self.__calculate_index(name_string)
        table_element = self.name_table[index]
        if table_element is None:
            return None
        else:
            # dict.keys() and dict.values() have the same order as long as
            # the dict is not being changed
            try:
                name_index = list(table_element.values()).index(name_string)
            # Exception is raised if name_string not in the list
            except ValueError:
                return None
            else:
                key = list(table_element.keys())[name_index]
                name_id = str(index) + str(key)
                return name_id

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        ids = []
        for str in name_string_list:
            if self.query(str) is None:
                self.__add_name_string(str)
            else:
                ids.append(self.query(str))

        return ids

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        index = int(name_id[:3])
        key = int(name_id[3:])

        table_element = self.name_table[index]
        if table_element is None:
            return None
        else:
            return table_element.get(key)  # returns None if not found

    def __add_name_string(self, name_string):
        """Add name_string to the name table."""
        index = self.__calculate_index(name_string)
        table_element = self.name_table[index]
        if table_element is None:
            self.name_table[index] = {self.name_counter: name_string}
        else:
            table_element[self.name_counter] = name_string
        self.name_counter += 1

    def __calculate_index(self, str):
        """Return the index of the list where string is going to be stored."""
        # Calculate index by summing ASCII values of the characters in str
        index = sum(ord(c) for c in str) % self.name_table_size

        return index
