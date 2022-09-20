#!/usr/bin/python3

# testing file

import ast
from voxpyastparser import astparser

###### setup 
# create the parser
vox_parser = astparser()

####### testing assignment statement
test_statement = "c = 3 - x * y"

print("Testing statement: ", test_statement)

tree = ast.parse(test_statement)
speech2 = vox_parser.emit(tree)

print("Returned text is ", speech2.text)
print("Returned data is ", speech2.data)
print()

####### testing if-else statement
test_statement = """
if x == 3:
  return 4
else:
  return 5
"""

print("Testing statement: ", test_statement)

tree = ast.parse(test_statement)
speech2 = vox_parser.emit(tree)

print("Returned text is ", speech2.text)
print("Returned data is", speech2.data)
