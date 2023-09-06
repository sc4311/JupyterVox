# add antlr2pyast to module search path
import os
parser_path = os.path.abspath('../antlr2pyast/')
import sys
sys.path.append(parser_path)

# antlr4 python packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
#from antlr_parser import *
from antlr_parser.Python3Parser import Python3Parser

##### AST tree print functions ###############
# generate the AST tree
def generate_ast_tree(stmt):
  input_stream = antlr4.InputStream(stmt)
  lexer = Python3Lexer(input_stream)
  stream = antlr4.CommonTokenStream(lexer)
  parser = Python3Parser(stream)
  tree = parser.single_input()

  return tree

# print a tree node
# this is a recursive function
def print_ast_tree_node(node, level):
  out_str = ""

  # print indents
  indent = "    "
  for i in range(level):
    out_str += indent

  # print the tree node
  #out_str += type(node).__name__
  out_str += str(type(node))#.__name__

  # Non-terminal nodes has more info and children to print
  if not isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
    out_str += "(Rule: " + str(node.getRuleIndex()) + ")"
    out_str += "(children: " + str(len(node.children)) + ")"
  else: # if terminal node, we need its type
    out_str += ": " + node.getText()
    out_str += str(node.symbol)

  # print the output string
  print(out_str)

  # print children
  for i in range(node.getChildCount()):
    print_ast_tree_node(node.getChild(i), level+1)

  return

# print out an AST tree
def print_ast_tree(ast_tree):
  print_ast_tree_node(ast_tree, 0)

  return


############# tree printing ################
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--statement', help='Statement to be parsed',
                    dest='stmt')
args = parser.parse_args()

tree = generate_ast_tree(args.stmt)

#tree.toStringTree(recog=parser)

print_ast_tree(tree)

