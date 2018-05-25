from scanner import Scanner
from names import Names
name = Names()
scan = Scanner("test.txt", name)

next_symbol = scan.get_symbol()
while next_symbol != [7, None]:
    #print(scan.name_string)
    print(next_symbol)
    next_symbol = scan.get_symbol()