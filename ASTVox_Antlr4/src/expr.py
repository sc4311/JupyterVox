# ANTLR4 to Python AST
# Conversion functions for the Expr* rules and terminals

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# generate AST node based on operator type
def gen_ast_operator(op_text):
    if op_text == "+":
        ast_node = ast.Add()
    elif op_text == "-":
        ast_node = ast.Sub()
    elif op_text == "*":
        ast_node = ast.Mult()
    elif op_text == "/":
        ast_node = ast.Div()
    elif op_text == "%":
        ast_node = ast.Mod()
    elif op_text == "@":
        ast_node = ast.MatMult()
    elif op_text == "//":
        ast_node = ast.FloorDiv()
    elif op_text == "**":
        ast_node = ast.Pow()
    elif op_text == "<<":
        ast_node = ast.LShift()
    elif op_text == ">>":
        ast_node = ast.RShift()
    elif op_text == "&":
        ast_node = ast.BitAnd()
    elif op_text == "^":
        ast_node = ast.BitXor()
    elif op_text == "|":
        ast_node = ast.BitOr()
    else:
        raise ValueError("Unknown operator in expression:" + op_text)

    return ast_node

#
def convert_expr(listener, ctx:Python3Parser.ExprContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Expr node has more than three children, count is " +
                         str(node.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() == 1:
        # one child => rule expr => atom_expr
        # copy child's AST node
        child = ctx.children[0]
        listener.pyast_trees[ctx] = listener.pyast_trees[child]
        return
    elif ctx.getChildCount() == 3:
        # three children typically is binary operation

        # generate the node for left and right children (operands) first
        left_opr = antlr2pyast.convert_tree(ctx.getChild(0))
        right_opr = antlr2pyast.convert_tree(ctx.getChild(2))

        # generat the operation node
        operator = gen_ast_operator(ctx.getChild(1).getText())

        # generate the tree node
        binop_node = ast.BinOp(left_opr, operator, right_opr)
        return binop_node
    else:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Expr node at the moment, count is " +
                                  str(node.getChildCount()))
