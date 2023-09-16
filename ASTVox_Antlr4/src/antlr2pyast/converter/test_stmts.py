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

# Convert not_test to Python AST node: astUaryOP, if it is "not" test;
# or the child's ast node, if it does not have "not" in it.
def convert_not_test(listener, ctx:Python3Parser.Not_testContext):
  '''
  Convert not_test to Python AST node: ast.UaryOP, if it is "not" test:
  or the child's ast node, if it does not have "not" in it.
  Rule:  not_test: 'not' not_test | comparison;
  '''
  
  if ctx.getChildCount() == 1:
    # for rule not_test: comparison, copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
  else:
    # for rule not_test: 'not' not_test, generate the ast.UnaryOp node
    ctx.pyast_tree = ast.UnaryOp(ast.Not(), ctx.children[1].pyast_tree)

  return

# Convert and_test to Python AST node: ast.BoolOp, if there is "and"; 
# or the child's ast node, if it does not have "and"
def convert_and_test(listener, ctx:Python3Parser.And_testContext):
  '''
  Convert and_test to Python AST node: ast.BoolOp, if there is "and"; 
  or the child's ast node, if it does not have "and"
  Rule: and_test: not_test ('and' not_test)*;
  '''
  
  # only handles one the case with one child now
  if ctx.getChildCount() == 1:  
    # rule and_test: not_test, copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
  else:
    # rule and_test: and_test: not_test ('and' not_test)+
    # translate to ast.BoolOp
    values = []
    # add the first operand to values
    values.append(ctx.children[0].pyast_tree)
    # add the rest of the operands
    for i in range(2, ctx.getChildCount(), 2):
      values.append(ctx.children[i].pyast_tree)
    # create the ast.BoolOp node
    ctx.pyast_tree = ast.BoolOp(ast.And(), values)
    
  return

# Convert and_test to Python AST node: ast.BoolOp, if there is "or"; 
# or the child's ast node, if it does not have "or"
def convert_or_test(listener, ctx:Python3Parser.Or_testContext):
  '''
  Convert or_test to Python AST node: ast.BoolOp, if there is "or"; 
  or the child's ast node, if it does not have "or".
  Rule: or_test: and_test ('or' and_test)*;
  '''

  # only handles one the case with one child now
  if ctx.getChildCount() == 1:  
    # rule or_test: and_test, copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
  else:
    # rule or_test: and_test: and_test ('or' and_test)+
    # translate to ast.BoolOp
    values = []
    # add the first operand to values
    values.append(ctx.children[0].pyast_tree)
    # add the rest of the operands
    for i in range(2, ctx.getChildCount(), 2):
      values.append(ctx.children[i].pyast_tree)
    # create the ast.BoolOp node
    ctx.pyast_tree = ast.BoolOp(ast.Or(), values)
    
  return


# Convert test to the corresponding Python AST node. If there is only or_test,
# copy the child's AST node; if there is 'if' ... 'else' ..., convert to
# ast.IfExp. lambdef is not handled yet?
def convert_test(listener, ctx:Python3Parser.TestContext):
  '''
  Convert test to the corresponding Python AST node. If there is only or_test,
  copy the child's AST node; if there is 'if' ... 'else' ..., convert to
  ast.IfExp. lambdef is not handled yet?
  Rule: test: or_test ('if' or_test 'else' test)? | lambdef;
  '''
  
  if ctx.getChildCount() == 1:
    # rule test: or_test | lambdef, copy child's AST node
    child = ctx.children[0]
    # listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
  else:
    # rule test: or_test ('if' or_test 'else' test)?, convert to ast.IfExp
    body = ctx.children[0].pyast_tree
    test = ctx.children[2].pyast_tree
    orelse = ctx.children[4].pyast_tree

    ctx.pyast_tree = ast.IfExp(test, body, orelse)
    
  return


# Convert comparison to child's tree (if only one child), or ast.Compare (if
# this is really a comparion)
def convert_comparison(listener, ctx:Python3Parser.ComparisonContext):
  '''
  Convert comparison to child's tree (if only one child), or ast.Compare (if
  this is really a comparison)
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

# convert testlist_comp to a list of AST nodes of test or star_expr
def convert_testlist_comp(listener, ctx:Python3Parser.Testlist_compContext):
  '''
  Convert testlist_comp to a list of AST nodes for test or star_expr.
  Rule: testlist_comp: (test|star_expr) ( comp_for | (',' (test|star_expr))* ','? );

  Only handles the case without comp_for, i.e,
  testlist_comp: (test|star_expr) ((',' (test|star_expr))* ','? );

  Returns a list of AST nodes
  '''

  # append each children's pyast_tree to the list
  test_list = []
  for child in ctx.children:
    if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
      # this is a ','
      continue

    if isinstance(child, Python3Parser.Comp_forContext):
      raise NotImplementedError("Comp for (async for loops) are not handled yet")

    # should be test or star_expr now
    test_list.append(child.pyast_tree)

  ctx.pyast_tree = test_list

  return
