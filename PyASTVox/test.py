#!/usr/bin/python3

# testing file

import ast
from voxpyastparser import astparser

###### setup 
# create the parser
vox_parser = astparser()

def run_test(parser, statement):
    print("> Testing statement: ", statement)

    tree = ast.parse(statement)
    speech2 = parser.emit(tree)

    print("Returned text is ", speech2.text)
    print("Returned data is ", speech2.data)
    print()

    parser.text_to_speech(speech2.text)

    return

####### testing assignment statements
# test_statements = ["c = 3 - x ** y", "x = -12", "c -= a", "x += 10", "u *= 12",
#                    "t = \"hello\"",
#                    "c = 3*7 + a*b"]

# for s in test_statements:
#     run_test(vox_parser, s)

# ######## testing if-else statement
# test_statement = """
# if x == 3:
#   return 4
# else:
#   return 5
# """

# run_test(vox_parser, test_statement)

####### testing for-loop statement
test_statements = ["for _ in range(10): return",
                   "for i in [1, 1, 1]: return", 
                   "for i in 'Computer Science': sum += 0",
                   "for i in range(3, 10): print(i)", 
                   "for i in range (10, 0, -2): print(i)",
                   "for i in range (0, 10, 2): print(i)",
                   "for word in range(len('Python')): return",
                   "for x in ['University', 'of', 'Texas', 'at', 'San', 'Antonio']: return"]

for s in test_statements:
  run_test(vox_parser, s)
