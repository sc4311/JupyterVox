# Listener class for converting ANTLR4 AST tree to Python AST tree.
# This class follows the standard Listener interface of ANTLR4.
# For readability, the actual implementation of the member methods are
# provided in separate Python files

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# Actual implementation of the member methods
from . import atom_name_terminals
from . import expr
from . import basic_rules

class antlr2pyast_listener(Python3ParserListener):
    def __init__(self):
        #self.pyast_trees = {}

        return
        
    # Exit a parse tree produced by Python3Parser#atom.
    def exitAtom(self, ctx:Python3Parser.AtomContext):
        atom_name_terminals.convert_atom(self, ctx)

    # Exit a parse tree produced by Python3Parser#name.
    def exitName(self, ctx:Python3Parser.NameContext):
        atom_name_terminals.convert_name(self, ctx)

    # Exit a parse tree produced by Python3Parser#atom_expr.
    def exitAtom_expr(self, ctx:Python3Parser.Atom_exprContext):
        atom_name_terminals.convert_atom_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#expr.
    def exitExpr(self, ctx:Python3Parser.ExprContext):
        expr.convert_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#comparison.
    def exitComparison(self, ctx:Python3Parser.ComparisonContext):
        basic_rules.convert_comparison(self, ctx)

    # Exit a parse tree produced by Python3Parser#not_test.
    def exitNot_test(self, ctx:Python3Parser.Not_testContext):
        basic_rules.convert_not_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#and_test.
    def exitAnd_test(self, ctx:Python3Parser.And_testContext):
        basic_rules.convert_and_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#or_test.
    def exitOr_test(self, ctx:Python3Parser.Or_testContext):
        basic_rules.convert_or_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#test.
    def exitTest(self, ctx:Python3Parser.TestContext):
        basic_rules.convert_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist_star_expr.
    def exitTestlist_star_expr(self,
                               ctx:Python3Parser.Testlist_star_exprContext):
        basic_rules.convert_testlist_star_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#expr_stmt.
    def exitExpr_stmt(self, ctx:Python3Parser.Expr_stmtContext):
        basic_rules.convert_expr_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmt.
    def exitSimple_stmt(self, ctx:Python3Parser.Simple_stmtContext):
        basic_rules.convert_simple_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmts.
    def exitSimple_stmts(self, ctx:Python3Parser.Simple_stmtsContext):
        basic_rules.convert_simple_stmts(self, ctx)

    # Exit a parse tree produced by Python3Parser#single_input.
    def exitSingle_input(self, ctx:Python3Parser.Single_inputContext):
        basic_rules.convert_single_input(self, ctx)
