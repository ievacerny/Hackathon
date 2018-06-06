"""Test helper function for test_scanner. Not actually used in the product."""
testcases = [
    ("DEVICES:\nCLOCK CL3 3,", "Line 2: CLOCK CL3 3,\n",
        False, True, 4),
    ("DEVICES:\nCLOCK\nCL3\n3,", "CL3\n",
        False, True, 4),
    ("DEVICES:\nCLOCK\n\tCL3\n3,", "\tCL3\n",
        False, True, 4),
    ("DEVICES:\nCLOCK\n\n\n\tCL3\n3,", "\tCL3\n",
        False, True, 4),
    ("DEVICES:\nCLOCK CL3 3,", "CLOCK CL3 3,\n        ^\n",
        False, False, 4),
    ("DEVICES:\n\tCLOCK CL3 3,", "\tCLOCK CL3 3,\n\t        ^\n",
        False, False, 4),
    ("DEVICES:\nCLOCK\n\nCL3 3,", "CL3 3,\n  ^\n",
        False, False, 4),
    ("DEVICES:\nCLOCK CL3 3,", "CLOCK CL3 3,\n    ^\n",
        True, False, 4),
    ("DEVICES:\nCLOCK\tCL3 3,", "CLOCK\tCL3 3,\n    ^\n",
        True, False, 4),
    ("DEVICES:\n\tCLOCK\tCL3 3,", "\tCLOCK\tCL3 3,\n\t    ^\n",
        True, False, 4),
    ("DEVICES:\nCLOCK  .  CL3 3,", "CLOCK  .  CL3 3,\n       ^\n",
        True, False, 5),
    ("DEVICES:\nCLOCK \*Com*\ CL3 3,", "CLOCK \*Com*\ CL3 3,\n    ^\n",
        True, False, 4),
    ("DEVICES:\n\tCLOCK \*Com*\ CL3 3,",
        "\tCLOCK \*Com*\ CL3 3,\n\t    ^\n",
        True, False, 4),
    ("DEVICES:\n\tCLOCK\t\*Com*\CL3 3,",
        "\tCLOCK\t\*Com*\CL3 3,\n\t    ^\n",
        True, False, 4),
    ("DEVICES:\n\tCLOCK\*\tCom*\CL3 3,",
        "\tCLOCK\*\tCom*\CL3 3,\n\t    ^\n",
        True, False, 4),
    ("DEVICES:\nCLOCK \*CLOCK*\ CL3 3,", "CLOCK \*CLOCK*\ CL3 3,\n    ^\n",
        True, False, 4),
    ("DEVICES:\nCLOCK *CLOCK* CL3 3,",
        "CLOCK *CLOCK* CL3 3,\n            ^\n",
        True, False, 7),
    ("DEVICES:\nCLOCK \CLOCK\ CL3 3,",
        "CLOCK \CLOCK\ CL3 3,\n            ^\n",
        True, False, 7),
    ("DEVICES:\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
        True, False, 3),
    ("DEVICES:\n\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
        True, False, 3),
    ("\tDEVICES:\nCLOCK CL3 3,", "\tDEVICES:\n\t       ^\n",
        True, False, 3),
    ("DEVICES:\n\\\\Comment\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
        True, False, 3),
    ("DEVICES:\n\\\nCLOCK CL3 3,", "\\\n^\n",
        True, False, 4),
    ("DEVICES:\n\\Comm\nCLOCK CL3 3,", "\\Comm\n    ^\n",
        True, False, 5),
    ("DEVICES:\\*Com\nment\n*\\CLOCK CL3 3,", "DEVICES:\\*Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\\*Com\nment\n*CLOCK *\\CLOCK CL3 3,",
        "DEVICES:\\*Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\\*Com\nment\n\\CLOCK *\\CLOCK CL3 3,",
        "DEVICES:\\*Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\\*Com\nment\n\\CLOCK *\\CLOCK*\\ CL3 3,",
        "\\CLOCK *\\CLOCK*\\ CL3 3,\n               ^\n",
        True, False, 6),
    ("DEVICES:\\*Com\\*\nment\n\\CLOCK *\\CLOCK*\\ CL3 3,",
        "\\CLOCK *\\CLOCK*\\ CL3 3,\n               ^\n",
        True, False, 6),
    ("DEVICES:\\*Com\nment\n\\CLOCK *\\*\\CLOCK CL3 3,",
        "DEVICES:\\*Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\\*C\nom\n\n*\\CLOCK CL3 3,", "DEVICES:\\*C\n       ^\n",
        True, False, 3),
    ("DEVICES:\n\\\\DEVICES:com\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
        True, False, 3),
    ("DEVICES:\n\\\\DEVICES:com\n\nCLOCK CL3 3,", "DEVICES:\n       ^\n",
        True, False, 3),
    ("\\*C\nom*\\DEVICES:\nCLOCK CL3 3,",
        "om*\\DEVICES:\n           ^\n",
        True, False, 3),
    ("DEVICES:\\*Com\nment\n*\\CLOCK CL3 3,", "DEVICES:\\*Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\n*Comm\n*CLOCK CL3 3,", "*CLOCK CL3 3,\n^\n",
        True, False, 6),
    ("DEVICES:\n*Comm\n*CLOCK CL3 3,", "*Comm\n    ^\n",
        True, False, 5),
    ("DEVICES:\\\\Com\nCLOCK CL3 3,", "DEVICES:\\\\Com\n       ^\n",
        True, False, 3),
    ("DEVICES:\\\\*Com\nCLOCK CL3 3,", "DEVICES:\\\\*Com\n       ^\n",
        True, False, 3)
]

for testcase in testcases:
    print("-----------------------------------------------------------")
    print("\t\t\tData", str(testcase[4]), str(testcase[2]), str(testcase[3]),
          "\n" + testcase[0])
    print("\t\t\tOutput\n" + testcase[1])
