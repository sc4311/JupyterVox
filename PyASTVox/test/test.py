#!/usr/bin/python3

# testing file

import ast

# help import sibling directories
import sys
sys.path.append("../vox_pyast_parser")

from astparser import astparser
from speech import Speech

# create the parser
vox_parser = astparser()

tree = ast.parse("3 + 4")
s = vox_parser.emit(tree)

print(s.text)
print(s.data)
