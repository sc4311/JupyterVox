# Antlr4 to Python AST
# Conversion function for control flow statements, including
#   flow_stmt
#   if_stmt
#   return

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# convert Return_stmt to ast.Return
# rule: return_stmt: 'return' testlist?;
def convert_return(listener, ctx:Python3Parser.Return_stmtContext):
  # retrieve the return value
  if ctx.getChildCount() == 1:
    # return without return value
    value = None
  elif ctx.getChildCount() == 2:
    # return has values 
    value = tools.list_to_node_or_tuple(ctx.children[1].pyast_tree,
                                        is_load=True)
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

# Convert BlockContext to the "body" field in Python AST nodes.
def convert_block_to_body(block:Python3Parser.BlockContext):
  '''
  Convert BlockContext to the "body" field in Python AST nodes.
  In Python AST nodes, the "body" is usually a list. However, the BlockContext's
  pyast_tree may be a single tree node if there is only one statement in the 
  block. Hence the conversion. 
  Returns the list for "body".

  Note: this function may not be necessary. Block's pyast_tree seems to
  be always a list.
  '''
  
  if type(block.pyast_tree) is list:
      return block.pyast_tree
  else:
      # block is not a list, convert to list
      return [block.pyast_tree]

# convert if_stmt to ast.If
def convert_if_stmt(listener, ctx:Python3Parser.If_stmtContext):
  '''
  convert if_stmt to ast.If
  rule: if_stmt: 'if' test ':' block ('elif' test ':' block)* ('else' ':' block)?;

  Because Python AST treat elIf* as nested, we also need to construct the tree
  recursively
  '''

  # get the top level of test and body
  test = ctx.children[1].pyast_tree
  body = convert_block_to_body(ctx.children[3])

  # construct the ast.If node for the top level, ignore 'orelse" for now
  top_if_node = ast.If(test, body, [])
  ctx.pyast_tree = top_if_node

  # if there is no elif or else, just return
  if ctx.getChildCount() == 4:
    return

  # process the elif and else until the list is done
  i = 4 # index to read children of if_stmt
  pre_if_node = top_if_node # previous level of ast.If node
  while True:
    if ctx.children[i].getText() == "elif":
      # elif translates to another ast.If node
      test = ctx.children[i+1].pyast_tree
      body = convert_block_to_body(ctx.children[i+3])
      cur_if_node = ast.If(test, body, [])

      # append current if node to previous if node's orelse field
      pre_if_node.orelse = [cur_if_node]

      # prepare for next level of ast.If node
      pre_if_node = cur_if_node
      i = i + 4 # advance to next elif or else block

    elif ctx.children[i].getText() == "else":
      # append the "else"  body to previous level's ast.If node's orelse
      body = convert_block_to_body(ctx.children[i+2])
      pre_if_node.orelse = body
      break

    else:
      raise ValueError("Keyword is not elif or else, but " + 
                       ctx.children[i].getText())
