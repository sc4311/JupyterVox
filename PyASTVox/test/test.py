#!/usr/bin/python3

# testing file

import ast
import argparse
import traceback

# import sibling directories
import sys
sys.path.append("../pyastvox")
sys.path.append("../../ASTVox_Antlr4/src/antlr2pyast/")

# load the Vox parser
import utils

# import JVox speech generator
from jvox_screenreader import jvox_screenreader

def read_test_case(file_handle):
    # read line by line, and parse/check each line
    test_case_cnt = 0
    correct_cnt = 0
    incorrect_test_cases = []
    cannot_parse_cnt = 0
    cannot_parse_test_cases = []
    for line in file_handle:
        # remove leading  white space, as Python AST cannot handle it. 
        # this is reasonable, since indentation has meaning
        no_white_line = line.lstrip()
        if no_white_line == "":
            continue # skip empty line

        # preprocess the line to replace \n, \t with the actual \n and \t
        line = line.replace("\\n", '\n')
        line = line.replace("\\t", '\t')
        if line.startswith('#'): # comments, skip
            continue;

        # found a line that works
        return line

    # end of file
    return ""

# parse the input
parser = argparse.ArgumentParser(description='Testing file for JupyterVox with PyAST')

parser.add_argument('-f', '--file', metavar='FILE', dest='test_case_file',
                    help='path to the test case file')

parser.add_argument('-s', '--stmt', metavar='STATEMENT', dest='stmt',
                    help='a single statement to parse')

parser.add_argument('-v', '-verbose', dest='verbose', action='store_true',
                    help='enable verbose output')

parser.add_argument('-p', '--use_pyast', dest='use_pyast', action='store_true',
                    help='whether to use python AST for parsing; default use ANTRL4')

args = parser.parse_args()

if (args.test_case_file is None) and (args.stmt is None):
    print("Please specific test case file or statement")
    exit(1)

    
# create the parser
jvox = jvox_screenreader(not args.use_pyast)

if not args.stmt is None:
    # parse a single statement
    speech = jvox.generate_for_one(args.stmt, args.verbose)
    print("*  ", args.stmt, "=>", speech, "\n")
else:
    # parse a test case file
    # open the file
    if args.verbose:
        print("Processing test case file:", args.test_case_file, "\n")
          
    f = open(args.test_case_file, "r")

    # generate speech for each line
    print("Generating speeches ...\n")
    file_all_parsed = False
    while not file_all_parsed:
        test_case = read_test_case(f)

        if test_case == "": # no more test cases
            break
        
        speech = jvox.generate_for_one(test_case, args.verbose)
        
        print(">>> Test case:\n", test_case, "=>", speech, '\n')

    print("\nDone.")

    f.close()
