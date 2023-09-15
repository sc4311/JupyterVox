# Antlr4 to Python AST
# Conversion function for control test* statements, including
#   testlist
#   testlist_star_expr
#   not_test
#   and_test
#   or_test
#   test
#   compare
#   comp_op

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# convert testlist to a list of tests
# rule: testlist: test (',' test)* ','?;
def convert_testlist(listener, ctx:Python3Parser.TestlistContext):

  # if ctx.getChildCount() == 1:
  #   # only one child, use the child Python AST node
  #   ctx.pyast_tree = ctx.children[0].pyast_tree
  # else:
  
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


# Convert comparison to child's tree (if only one child), or ast.Compare (if
# this is really a comparion)
def convert_comparison(listener, ctx:Python3Parser.ComparisonContext):
    '''
    Convert comparison to child's tree (if only one child), or ast.Compare (if
    this is really a comparion)
    rule: comparison: expr (comp_op expr)*;
    '''

    if ctx.getChildCount() == 1:
        # just one child, copy child's AST node
        child = ctx.children[0]
        #listener.pyast_trees[ctx] = listener.pyast_trees[child]
        ctx.pyast_tree = child.pyast_tree

    else:
        # more than one child, need to convert to ast.Compare
        # get the left field
        left = ctx.children[0].pyast_tree

        # get the rest of the operators and comparators
        ops = []
        comparators = []
        for i in range(1, ctx.getChildCount(), 2):
          ops.append(ctx.children[i].pyast_tree)
          comparators.append(ctx.children[i+1].pyast_tree)

        # construct the ast.Compare node
        ctx.pyast_tree = ast.Compare(left, ops, comparators)
    
    return

# Convert comp_op to ast.Eq, ast.NotEq ...
def convert_comp_op(listener, ctx:Python3Parser.Comp_opContext):
  '''
  Convert comp_op to ast.Eq, ast.NotEq ...
  comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not';
  '''

  child = ctx.children[0]
  # generate compare operator node 
  if child.getText() == '<':
    op_node = ast.Lt()
  elif child.getText() == '>':
    op_node = ast.Gt()
  elif child.getText() == '==':
    op_node = ast.Eq()
  elif child.getText() == '>=':
    op_node = ast.GtE()
  elif child.getText() == '<=':
    op_node = ast.LtE()
  elif child.getText() == '<>':
    op_node = ast.NotEq()
  elif child.getText() == '!=':
    op_node = ast.NotEq()
  elif child.getText() == 'in':
    op_node = ast.In()
  elif child.getText() == 'not': # should be not in
    op_node = ast.NotIn()
  elif child.getText() == 'is':
    if ctx.getChildCount() == 1: #"is"
      op_node = ast.Is()
    else: # "is" "not"
      op_node = ast.IsNot() 

  ctx.pyast_tree = op_node

  return
