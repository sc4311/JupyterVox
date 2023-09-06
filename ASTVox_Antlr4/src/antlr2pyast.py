# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

# PyAST package
import ast

# node/rule-specific translation functions
from antlr2pyast_listener import anltr2pyast_listener

# generate the AST tree
def generate_ast_tree(stmt):
  input_stream = antlr4.InputStream(stmt)
  lexer = Python3Lexer(input_stream)
  stream = antlr4.CommonTokenStream(lexer)
  parser = Python3Parser(stream)
  tree = parser.single_input()

  return tree

# convert_tree: the main entrance function
# It uses the listener class to walk and convert the ANTLR4 tree
# Returns the Python AST tree and the listener class holding the Python AST tree
def convert_tree(tree):
    converter = anltr2pyast_listener()
    walker = antlr4.ParseTreeWalker()

    # traverse and convert the
    walker.walk(converter, tree)

    # get the converted tree
    pyast_tree = converter.pyast_trees[tree]

    return pyast_tree, converter

# deprecated implementation
# convert_tree: the main entrance function
# It calls the convert function for each type of nodes
# def convert_tree(node):
#     if isinstance(node, Python3Parser.NameContext):
#         ast_node = convert_name(node)
#     elif isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
#         ast_ndoe = convert_terminal(node)
#     elif isinstance(node, Python3Parser.AtomContext):
#         ast_node = convert_atom(node)
#     elif isinstance(node, Python3Parser.Atom_exprContext):
#         ast_node = convert_atom_expr(node)
#     elif isinstance(node, Python3Parser.ExprContext):
#         ast_node = convert_expr(node)
#     elif isinstance(node, Python3Parser.ComparisonContext):
#         ast_node = convert_comparison(node)
#     elif isinstance(node, Python3Parser.Not_testContext):
#         ast_node = convert_not_test(node)
#     elif isinstance(node, Python3Parser.And_testContext):
#         ast_node = convert_and_test(node)
#     elif isinstance(node, Python3Parser.Or_testContext):
#         ast_node = convert_or_test(node)
#     elif isinstance(node, Python3Parser.TestContext):
#         ast_node = convert_test(node)
#     elif isinstance(node, Python3Parser.Testlist_star_exprContext):
#         ast_node = convert_testlist_star_expr(node)
#     elif isinstance(node, Python3Parser.Expr_stmtContext):
#         ast_node = convert_expr_stmt(node)
#     elif isinstance(node, Python3Parser.Simple_stmtContext):
#         ast_node = convert_simple_stmt(node)
#     elif isinstance(node, Python3Parser.Simple_stmtsContext):
#         ast_node = convert_simple_stmts(node)
#     elif isinstance(node, Python3Parser.Single_inputContext):
#         ast_node = convert_single_input(node)
#     else:
#         raise TypeError("Unknown node type: " + str(type(node)))

    # return ast_node
