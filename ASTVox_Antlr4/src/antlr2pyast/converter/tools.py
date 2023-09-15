# Antlr4 to Python AST
# Tool functions

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# Recursively set the load/store context for node and all children 
def update_load_store(node:ast.AST, is_load = True):
  '''
  Recursively set the load/store context for node and all children 
  '''

  # set load/store for this node
  load_or_store = ast.Load() if is_load else ast.Store()
  if hasattr(node, 'ctx'):
      node.ctx = load_or_store

  # set load/store for children
  for field, value in ast.iter_fields(node):
        #print(field, "<xxxx>", value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    update_load_store(item, is_load)
        elif isinstance(value, ast.AST):
            update_load_store(value, is_load)

  return

# generate the Python AST node for testlist_star_expr, when it is used as a
# target or value in expressions
def testlistStarExpr_to_target_value(
    ctx:Python3Parser.Testlist_star_exprContext,
    is_load = True):
  '''
  Generate the Python AST node for testlist_star_expr, when it is used as a
  target or value in assignment statements.
  If one item in testlist_star_expr, return that item's Python AST node.
  If more then one items, return a ast.Tuple.
  '''

  # need to correct the load/store context for all children
  load_or_store = ast.Load() if is_load else ast.Store()
  for n in ctx.pyast_tree:
    update_load_store(n, is_load)

  if len(ctx.pyast_tree) == 1:
    ast_node = ctx.pyast_tree[0]
  else:
    ast_node = ast.Tuple(ctx.pyast_tree, load_or_store)

  return ast_node
