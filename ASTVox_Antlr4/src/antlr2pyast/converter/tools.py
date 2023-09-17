# Antlr4 to Python AST
# Tool functions

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast
# import traceback

# Recursively set the load/store context for node and all children 
def update_load_store(node:ast.AST, is_load = True):
  '''
  Recursively set the load/store context for node and all children 
  '''
  # if isinstance(node, ast.comprehension):
  #  print("updating", node, "Load:", is_load)
  #  for line in traceback.format_stack():
  #      print(line.strip())

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

# Convert a list of Python AST nodes into a single AST node
# or an ast.Tuple.
def list_to_node_or_tuple(
    nodes:list,
    is_load = True,
    update_children = True):
  '''
  Convert a list of Python AST nodes into a single AST node or an ast.Tuple.
  This is usually needed when the list is used as a target or value of an AST
  node.
  If there is one item in the list, return that item's Python AST node.
  If there are more then one items, return a ast.Tuple.
  '''
  # get the load/store context
  load_or_store = ast.Load() if is_load else ast.Store()
  # if asked, correct the load/store context for all children
  if update_children:
    for n in nodes:
      update_load_store(n, is_load)

  if len(nodes) == 1:
    ast_node = nodes[0]
  else: 
    ast_node = ast.Tuple(nodes, load_or_store)

  return ast_node
