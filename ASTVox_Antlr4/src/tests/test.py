# set module search path
import os
ast2pyast_path = os.path.abspath('../antlr2pyast/')
import sys
sys.path.append(ast2pyast_path)

# system packages
import argparse
import re
import traceback

# AST tree generation/conversion packages
from converter import antlr2pyast
import ast

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

############ functions for processing a test case
# generate and convert the AST tree from Antlr4, and return the printed tree
def test_antlr4_conversion(line):
    # generate and convert tree
    tree = antlr2pyast.generate_ast_tree(line)
    converted_tree, converter = antlr2pyast.convert_tree(tree)
    # print the tree
    converted_tree_str = []
    ast_visit(converted_tree, converted_tree_str)

    return converted_tree_str

# generate the AST tree with Python AST, and return the print tree
def test_pyast(line):
    # generate the tree
    pyast_tree = ast.parse(line)
    # print the tree
    pyast_tree_str = []
    ast_visit(pyast_tree, pyast_tree_str)

    return pyast_tree_str

############### functions for comparing two tree outputs

def are_nodes_same(node1:str, node2:str):
    '''
    Compare if two node output are the same.
    Return True if same, False is not
    '''
    # Notes:
    # 1. Need to remove object address when comparing

    # strip white spaces
    node1 = node1.strip()
    node2 = node2.strip()

    # remove object address with format "0xXXXXXXX..."
    addr_regex="0x[0-9a-f]+"
    node1 = re.sub(addr_regex, '', node1)
    node2 = re.sub(addr_regex, '', node2)

    # compare strings
    same = (node1 == node2)

    return same

# compare if two trees are the same
tree2_start_col = 50 # beginning position (in chars/cols) to print tree2
def compare_and_print_trees(tree1, tree2, print_tree):
    # make the two tree has the same height
    # if len(tree1) < len(tree2):
    #     tree2 = tree2[-len(tree1):]
    # else:
    #     tree1 = tree1[-len(tree2):]

    # print two trees out
    same_tree = True
    for i in range(len(tree1)):
        # compare if two trees are the same or not at this line
        same = "Same"
        if not are_nodes_same(tree1[i], tree2[i]):
            same = "Diff"
            same_tree = False
        if print_tree: print(str(same) + ":  ", end='')    
            
        # print tree1
        if print_tree: print(tree1[i], end='')
        # skip to beginning col of tree2
        skip = ' ' * (tree2_start_col - len(tree1[i]))
        # print tree2
        if print_tree: print(skip + tree2[i])

    return same_tree

def print_converted_tree(tree1):
    for i in range(len(tree1)): 
        # print tree1
        print(tree1[i])
    return

# convert the tree and compare with the standard Python AST tree
# returns if
def convert_and_compare(stmt, test_case_cnt, print_tree):

    # print test case first
    print("Test case", test_case_cnt, ":", stmt.rstrip('\n'))
    

    # generate the tree/outputs for converted tree
    try:
        converted_tree_str = test_antlr4_conversion(stmt)
        antlr4_parse_error = False
    except Exception as e:
        # parsing error, this could be due to a completely unparse-able
        # partial statement, e.g., "else:\n"
        antlr4_parse_error = True
        traceback.print_exc()
        #print(e)

    # generate the tree/outputs for Python AST tree
    try:
        pyast_tree_str = test_pyast(stmt)
        pyast_parse_erred = False
    except:
        # Python AST parsing error should only have for
        # partial compound statements. We should still be
        # able to handle these statements.
        # print("Python AST Parsing error")
        pyast_parse_erred = True

    if pyast_parse_erred and antlr4_parse_error:
        # both parsing error, skip this one
        same_tree = None
    elif pyast_parse_erred and (not antlr4_parse_error):
        # Only Python AST parsing error, assume the comparison is correct
        same_tree = True
        # print our tree if asked
        if print_tree:
            print_converted_tree(converted_tree_str)
        print("Test case", test_case_cnt, "passed:", same_tree,
              ", Note: Python AST parsing error, assume passing")
        print()
    elif (not pyast_parse_erred) and antlr4_parse_error:
        # only antlr4 parsing error, assume the comparison is incorrect
        same_tree = False
    else:
        # both parsings are correct
        # if Python parsing has no error, print and compare trees
        same_tree = compare_and_print_trees(pyast_tree_str, converted_tree_str,
                                            print_tree)
        print("Test case", test_case_cnt, "passed:", same_tree)
        print()

    return same_tree, pyast_parse_erred, antlr4_parse_error
    


####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='test case file',
                    dest='filename')
parser.add_argument('-s', '--statement', help='a single statement to test',
                    dest='stmt')
parser.add_argument('-p', '--print-tree', action='store_true',
                    dest='print_tree', help='enable AST tree printing' )
args = parser.parse_args()

if not (args.stmt is None):
    convert_and_compare(args.stmt, 0, args.print_tree)

if not (args.filename is None):
    # open test case file
    test_f = open(args.filename, 'r')

    # read line by line, and parse/check each line
    test_case_cnt = 0
    correct_cnt = 0
    incorrect_test_cases = []
    cannot_parse_cnt = 0
    cannot_parse_test_cases = []
    for line in test_f:
        # remove leading  white space, as Python AST cannot handle it. 
        # this is reasonable, since indentation has meaning
        line = line.lstrip()
        if line == "":
            continue # skip empty line

        # preprocess the line to replace \n, \t with the actual \n and \t
        line = line.replace("\\n", '\n')
        line = line.replace("\\t", '\t')
        if line.startswith('#'): # comments, skip
            continue;

        same_tree, pyast_parse_erred, antlr4_parse_error = convert_and_compare(
            line, test_case_cnt, args.print_tree)
        if same_tree is None:
            # both parsing failed
            cannot_parse_cnt += 1
            cannot_parse_test_cases.append(line)
        elif same_tree:
            # conversion is correct
            correct_cnt += 1
            test_case_cnt += 1
        else:
            incorrect_test_cases.append(line)
            test_case_cnt += 1

    # print out overall results
    print("Correct/Total: {0}/{1}".format(correct_cnt, test_case_cnt))
    if correct_cnt < test_case_cnt:
        print("Incorrect test cases:")
        print(incorrect_test_cases)
    # print out cannot parse cases
    if cannot_parse_cnt != 0:
        print("Number of test cases cannot parse:", cannot_parse_cnt)
        print("Cannot parse test cases:")
        for s in cannot_parse_test_cases:
            print(s)	
    
    # close test case file
    test_f.close()
    
