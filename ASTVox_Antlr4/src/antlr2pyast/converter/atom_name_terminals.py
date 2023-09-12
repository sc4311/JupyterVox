# ANTLR4 to Python AST
# Conversion functions for the ATOM* rules, NAME rules and terminals

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# convert a NUMBER to ast.Constant
def gen_ast_constant(ctx:antlr4.tree.Tree.TerminalNodeImpl):
    # extract the value, a bit hacky
    try:
        value = int(ctx.getText())
    except ValueError:
        value = float(ctx.getText())

    # generate the AST node
    ast_node = ast.Constant(value)

    return ast_node

# It seems ANTLR4 will pass on the string with the quote marks, I will
# remove them here. However, there may be other preprocessing need, 
# hence the separate function
def atom_string_processing(text:str):
  if text[0] == '\"':
    return text.lstrip('\"').rstrip('\"')
  elif text[0] == '\'':
    return text.lstrip('\'').rstrip('\'')
  else:
    return text # should not reach here

# convert a list of strings (STRING+) to one string ast.Constant node
# note that, the strings will also be saved into a list and add to the
# ast.Constant node. The name of the string is "original_string"
def convert_atom_strings(listener, ctx:Python3Parser.AtomContext):
  
  combined_string=""
  original_strings=[]

  for child in ctx.children:
    # check if child is STRING
    if not (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.STRING):
      raise ValueError("")

    # combine and insert the strings.
    combined_string += atom_string_processing(child.getText())
    original_strings.append(child.getText())

  ast_node = ast.Constant(value = combined_string)
  ast_node.original_strings = original_strings

  return ast_node

# convert an atom node from Anltr4 tree to Python AST tree
def convert_atom(listener, ctx:Python3Parser.AtomContext):
    # should have more than one child and the type of the first child
    # can help determine what rule it is and what to do
    first_child = ctx.children[0]

    # process based on rules/first_child
    if isinstance(first_child, Python3Parser.NameContext):
        # rule 1: atom: name
        # child is a name node, just copy the child's AST tree
        ctx.pyast_tree = first_child.pyast_tree
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.NUMBER):
        # rule 2: atom: NUMBER
        # child a is NUMER type, convert it to ast.Constant
        ctx.pyast_tree = gen_ast_constant(first_child)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.STRING):
        # rule 3: atom: STRING+
        # child a is String type, convert it to list of strings
        ctx.pyast_tree = convert_atom_strings(listener, ctx)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.TRUE):
        # rule 4: atom: "True"
        # child a is True, convert it to ast.Constant
        # implement here => ast.Constant
        ctx.pyast_tree = ast.Constant(True)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.FALSE):
        # rule 4: atom: "True"
        # child a is False, convert it to ast.Constant
        # implement here => ast.Constant
        ctx.pyast_tree = ast.Constant(False)
    else:
        raise NotImplementedError("Other rules not implemented for " +
                                  "Atom node at the moment")
    return

# convert an name node from Anltr4 tree to Python AST tree
def convert_name(listener, ctx:Python3Parser.NameContext):
    # should have only one child
    if ctx.getChildCount() != 1:
        raise ValueError("Name node has more than one child, count is" +
                         str(ctx.getChildCount()))

    # child should be terminal
    child = ctx.children[0]
    if not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
        raise TypeError("Child of Name node is not a terminal type.")

    # generate the Python AST tree node
    # name : NAME | '_' | 'match' ; not sure what to do with '_'
    # and 'match'
    id = child.getText()
    # potential error: not sure how to determine if the operation is
    # store or del.
    ast_node = ast.Name(id, ast.Load())

    # save the node/tree
    # listener.pyast_trees[ctx] = ast_node
    ctx.pyast_tree = ast_node

    return

# Grammar: atom_expr: AWAIT? atom trailer*;
def convert_atom_expr(listener, ctx:Python3Parser.Atom_exprContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Atom_expr node has more than three children, " +
                         "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom_expr node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    #listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return
