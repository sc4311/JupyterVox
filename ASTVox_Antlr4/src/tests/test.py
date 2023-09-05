# fix module path issue
import os
parser_path = os.path.abspath('../antlr_parser/')
ast2pyast_path = os.path.abspath('../')
import sys
sys.path.append(parser_path)
sys.path.append(ast2pyast_path)

# system packages
import argparse

# AST tree generation/conversion packages
import antlr2pyast
import ast

####### functions to print an AST tree
def str_node(node):
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
    converted_tree = antlr2pyast.convert_tree(tree)
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
# compare if two trees are the same
# if one tree is taller than the other one, only the lower parts of the tree
# are compared
tree2_start_col = 40 # beginning position (in chars/cols) to print tree2
def compare_and_print_trees(tree1, tree2):
    # make the two tree has the same height
    if len(tree1) < len(tree2):
        tree2 = tree2[-len(tree1):]
    else:
        tree1 = tree1[-len(tree2):]

    # print two trees out
    same_tree = True
    for i in range(len(tree1)):
        # compare if two trees are the same or not at this line
        same = "Same"
        if tree1[i].strip() != tree2[i].strip():
            same = "Diff"
            same_tree = False
        print(str(same) + ":  ", end='')    
            
        # print tree1
        print(tree1[i], end='')
        # skip to beginning col of tree2
        skip = ' ' * (tree2_start_col - len(tree1[i]))
        # print tree2
        print(skip + tree2[i])

    return same_tree
    


####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='test case file',
                    dest='filename')
args = parser.parse_args()


# open test case file
test_f = open(args.filename, 'r')

# read line by line, and parse/check each line
test_case_cnt = 1
for line in test_f:
    line = line.rstrip('\n')
    # generate the tree/outputs for converted tree
    converted_tree_str = test_antlr4_conversion(line)
    #for s in converted_tree_str:
    #    print(s)

    # generate the tree/outputs for Python AST tree
    pyast_tree_str = test_pyast(line)
    #for s in pyast_tree_str:
    #    print(s)

    # print and compare trees
    print("Test case", test_case_cnt, ":", line)
    same_tree = compare_and_print_trees(pyast_tree_str, converted_tree_str)
    print("Test case", test_case_cnt, "passed:", same_tree)
    print()

    test_case_cnt += 1

# close test case file
test_f.close()
    
