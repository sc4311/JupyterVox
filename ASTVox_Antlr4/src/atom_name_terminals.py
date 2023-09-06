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

# convert an atom node with terminals to Python AST tree
def convert_atom_terminals(listener, ctx:Python3Parser.AtomContext):
    # should have only one child
    child = ctx.children[0]

    # process case by case
    if isinstance(child, Python3Parser.NameContext):
        # case 1: child is a name node, just copy the child's AST tree
        listener.pyast_trees[ctx] = listener.pyast_trees[child]
    elif (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.NUMBER):
        # case 2: child a is NUMER type, convert it to ast.Constant
        listener.pyast_trees[ctx] = gen_ast_constant(child)
    else:
        raise NotImplementedError("Other terminal type not implemented yet "
                                  "for Atom node at the moment")

    return

# convert an atom node from Anltr4 tree to Python AST tree
def convert_atom(listener, ctx:Python3Parser.AtomContext):
    # terminals
    if ctx.getChildCount() == 1:
        convert_atom_terminals(listener, ctx)
    else:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom node at the moment")
    return

# convert an name node from Anltr4 tree to Python AST tree
def convert_name(listener, ctx:Python3Parser.NameContext):
    # should have only one child
    if ctx.getChildCount() != 1:
        raise ValueError("Name node has more than one child, count is" +
                         str(node.getChildCount()))

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
    listener.pyast_trees[ctx] = ast_node

    return

# Grammar: atom_expr: AWAIT? atom trailer*;
def convert_atom_expr(listener, ctx:Python3Parser.Atom_exprContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Atom_expr node has more than three children, " +
                         "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom_expr node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    listener.pyast_trees[ctx] = listener.pyast_trees[child]
    return
