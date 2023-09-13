# Antlr4 to Python AST
# Conversion function for control flow statements, including
#   flow_stmt
#   return

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# convert Return_stmt to ast.Return
# rule: return_stmt: 'return' testlist?;
def convert_return(listener, ctx:Python3Parser.Return_stmtContext):
  # retrieve the return value
  if ctx.getChildCount() == 1:
    # return without return value
    value = None
  elif ctx.getChildCount() == 2:
    # return has values 
    if ctx.children[1].getChildCount() == 1:
      # only one return value, pass on the value's tree
      value = ctx.children[1].pyast_tree
    else:
      # more than one return values, put the return value in an ast.Tuple
      value = ast.Tuple(ctx.children[1].pyast_tree, ast.Load())
  else:
    raise ValueError("I though return_stmt can have 2 children at most, ",
                     "however the children count is", ctx.getChildCount())

  # create the ast.Return node
  ctx.pyast_tree = ast.Return(value)

  return

# convert a flow_stmt to ast.
# Flow is just a intermediate non-terminal, hence its Python AST copies its
# child.
# rule: flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt |
#                  yield_stmt;
def convert_flow_stmt(listener, ctx:Python3Parser.Flow_stmtContext):
  if ctx.getChildCount() != 1:
    raise ValueError("Flow_stmt has more than one child, child count is",
                     ctx.getChildCount())

  ctx.pyast_tree = ctx.children[0].pyast_tree

  return

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

    # create the Tuple node
    # return values should always be load, right?
    ctx.pyast_tree = ast.Tuple(list_tests, ast.Load())

  return
