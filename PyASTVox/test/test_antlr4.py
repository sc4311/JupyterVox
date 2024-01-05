#!/usr/bin/python3

# testing file

import ast
import argparse
import traceback

# import sibling directories
import sys
sys.path.append("../pyastvox")
# import ASTVox_Anltr4
sys.path.append("../../ASTVox_Antlr4/src/antlr2pyast/")

# load the Vox parser
import utils

# import JVox speech generator
from screenreader import pyastvox_speech_generator

# parser based on Antlr4
from converter import antlr2pyast

# function to read a test case from the file a test case in a file starts with a
# line of "<<<...", and ends with a line ">>>,,,".
#
# Note that this function does not check for incorrect formatting. So please
# make sure the test case file is correctly formatted.
def read_test_case_old(file_handle):
    # skip lines until a line of "<<<..."
    for line in file_handle:
        if line.startswith("<<<"):
           break

    # read-in the test  cases
    test_case = ""
    for line in file_handle:
        if not line.startswith(">>>"):
            test_case += line
        else:
            break

    return test_case

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

####### functions to print an AST tree
def str_node(node):
    #if isinstance(node, ast.Module):
        # for module, just print its class name and type_ignores
        # otherwise, the pointer addresses will never match between trees
        # s = "Module(type_ignores=" + repr(node.type_ignores) + ")"
        # return s   
    #elif isinstance(node, ast.AST):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)

# output node to out_str,and visit its children
def ast_visit(node, out_str, level=0):
    #print('  ' * level + str_node(node))
    out_str.append('  ' * level + str_node(node))
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    ast_visit(item, out_str, level=level+1)
        elif isinstance(value, ast.AST):
            ast_visit(value, out_str, level=level+1)

# generate the speech for one statement
def gen_speech_for_one(vox_gen, stmt, verbose):
    # remove lead white spaces, but keep the original statement for
    # white space reading.
    stmt_original = stmt
    stmt = stmt.lstrip()
    
    # first check if it is a standalone non-parse-able statement,
    # e.g., "try", "else", "except". They will be read without
    # parsing.
    standalone_speech = vox_gen.gen_standalone_statemetns(stmt)
    if standalone_speech != "":
        return standalone_speech
    
    # generate AST tree
    # tree = ast.parse(stmt)
    # generate and convert tree
    try:
        tree = antlr2pyast.generate_ast_tree(stmt)
        converted_tree, converter = antlr2pyast.convert_tree(tree)
    except Exception as e:
        # parsing error, this could be due to a completely unparse-able
        # partial statement, e.g., "else:\n"
        antlr4_parse_error = True
        if verbose:
            traceback.print_exc()
        return "Antlr4 Converter error for code"

    # print the tree
    if verbose:
        converted_tree_str = []
        ast_visit(converted_tree, converted_tree_str)
        for tree_line in converted_tree_str:
            print(tree_line)

    # generate speech
    try:
        vox_gen.generate(converted_tree)
    except Exception as e:
        # speech generation error, should not happen
        traceback.print_exc()
        return "JVox speech generate error"

    # generate whitespace speeches
    whitespace_speech = vox_gen.gen_leading_whitespace_speech(stmt_original)
    converted_tree.jvox_speech["whitespace"] =  whitespace_speech
        
    return converted_tree.jvox_speech


# parse the input
parser = argparse.ArgumentParser(description='Testing file for JupyterVox with PyAST')

parser.add_argument('-f', '--file', metavar='FILE', dest='test_case_file',
                    help='path to the test case file')

parser.add_argument('-s', '--stmt', metavar='STATEMENT', dest='stmt',
                    help='a single statement to parse')

parser.add_argument('-v', '-verbose', dest='verbose', action='store_true',
                    help='enable verbose output')

args = parser.parse_args()

if (args.test_case_file is None) and (args.stmt is None):
    print("Please specific test case file or statement")
    exit(1)

    
# create the parser
vox_gen = pyastvox_speech_generator()
vox_gen.set_speech_style(ast.BinOp, "alternatev2")

if not args.stmt is None:
    # parse a single statement
    speech = gen_speech_for_one(vox_gen, args.stmt, args.verbose)
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
        
        speech = gen_speech_for_one(vox_gen, test_case, args.verbose)
        
        print(">>> Test case:\n", test_case, "=>", speech, '\n')
        #print(s.data)

    print("\nDone.")

    f.close()
