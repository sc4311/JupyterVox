# Antlr4 to Python AST
# Conversion function for control test* statements, including
#   testlist
#   return

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# convert testlist to a single node or ast.Tuple list node (a list of tests)
# rule: testlist: test (',' test)* ','?;
def convert_testlist(listener, ctx:Python3Parser.TestlistContext):

  if ctx.getChildCount() == 1:
    # only one child, use the child Python AST node
    ctx.pyast_tree = ctx.children[0].pyast_tree
  else:
    # more than one child, create an ast.Tuple node to store the children
    list_tests = []
    for child in ctx.children:
      # need to check child, since ',' can also be a child
      if not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
        list_tests.append(child.pyast_tree)

    # return the list as the tree
    ctx.pyast_tree = list_tests
    
  return

# Grammar:
#    not_test: 'not' not_test | comparison;
def convert_not_test(listener, ctx:Python3Parser.Not_testContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Not_test node has more than three children, "
                         + "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Not_test node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# Grammar:
#   and_test: not_test ('and' not_test)*;
def convert_and_test(listener, ctx:Python3Parser.And_testContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("And_test node has more than three children, "
                         + "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "And_test node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# Grammar:
#    or_test: and_test ('or' and_test)*;
def convert_or_test(listener, ctx:Python3Parser.Or_testContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Or_test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Or_test node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# Grammar:
#    test: or_test ('if' or_test 'else' test)? | lambdef;
def convert_test(listener, ctx:Python3Parser.TestContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Test node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# Grammar:
#    testlist_star_expr: (test|star_expr) (',' (test|star_expr))* ','?;
def convert_testlist_star_expr(listener,
                               ctx:Python3Parser.Testlist_star_exprContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Testlist_star_expr node has more than three children"
                         + ", count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
      raise NotImplementedError("More than one child is not supported for " +
                                "Testlist_star_expr node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return
