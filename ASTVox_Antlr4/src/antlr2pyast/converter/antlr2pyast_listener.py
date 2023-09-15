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
from . import flow_stmts
from . import test_stmts
from . import loop_stmts

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
        test_stmts.convert_comparison(self, ctx)

    # Exit a parse tree produced by Python3Parser#not_test.
    def exitNot_test(self, ctx:Python3Parser.Not_testContext):
        test_stmts.convert_not_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#and_test.
    def exitAnd_test(self, ctx:Python3Parser.And_testContext):
        test_stmts.convert_and_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#or_test.
    def exitOr_test(self, ctx:Python3Parser.Or_testContext):
        test_stmts.convert_or_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#test.
    def exitTest(self, ctx:Python3Parser.TestContext):
        test_stmts.convert_test(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist_star_expr.
    def exitTestlist_star_expr(self,
                               ctx:Python3Parser.Testlist_star_exprContext):
        expr.convert_testlist_star_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#expr_stmt.
    def exitExpr_stmt(self, ctx:Python3Parser.Expr_stmtContext):
        expr.convert_expr_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmt.
    def exitSimple_stmt(self, ctx:Python3Parser.Simple_stmtContext):
        basic_rules.convert_simple_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#simple_stmts.
    def exitSimple_stmts(self, ctx:Python3Parser.Simple_stmtsContext):
        basic_rules.convert_simple_stmts(self, ctx)

    # Exit a parse tree produced by Python3Parser#single_input.
    def exitSingle_input(self, ctx:Python3Parser.Single_inputContext):
        basic_rules.convert_single_input(self, ctx)

    # Exit a parse tree produced by Python3Parser#return_stmt.
    def exitReturn_stmt(self, ctx:Python3Parser.Return_stmtContext):
        flow_stmts.convert_return(self, ctx)

    # Exit a parse tree produced by Python3Parser#flow_stmt.
    def exitFlow_stmt(self, ctx:Python3Parser.Flow_stmtContext):
        flow_stmts.convert_flow_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist.
    def exitTestlist(self, ctx:Python3Parser.TestlistContext):
        test_stmts.convert_testlist(self, ctx)

    # Exit a parse tree produced by Python3Parser#block.
    def exitBlock(self, ctx:Python3Parser.BlockContext):
        basic_rules.convert_block(self, ctx)

    # Exit a parse tree produced by Python3Parser#for_stmt.
    def exitFor_stmt(self, ctx:Python3Parser.For_stmtContext):
        loop_stmts.convert_for_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#exprlist.
    def exitExprlist(self, ctx:Python3Parser.ExprlistContext):
        expr.convert_exprlist(self, ctx)

    # Exit a parse tree produced by Python3Parser#compound_stmt.
    def exitCompound_stmt(self, ctx:Python3Parser.Compound_stmtContext):
        basic_rules.convert_compound_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#comp_op.
    def exitComp_op(self, ctx:Python3Parser.Comp_opContext):
        test_stmts.convert_comp_op(self, ctx)

    # Exit a parse tree produced by Python3Parser#while_stmt.
    def exitWhile_stmt(self, ctx:Python3Parser.While_stmtContext):
        loop_stmts.convert_while_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#if_stmt.
    def exitIf_stmt(self, ctx:Python3Parser.If_stmtContext):
        flow_stmts.convert_if_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#stmt.
    def exitStmt(self, ctx:Python3Parser.StmtContext):
        basic_rules.convert_stmt(self, ctx)

    # Exit a parse tree produced by Python3Parser#star_expr.
    def exitStar_expr(self, ctx:Python3Parser.Star_exprContext):
        expr.convert_star_expr(self, ctx)

    # Exit a parse tree produced by Python3Parser#testlist_comp.
    def exitTestlist_comp(self, ctx:Python3Parser.Testlist_compContext):
        test_stmts.convert_testlist_comp(self, ctx)

    # Exit a parse tree produced by Python3Parser#dictorsetmaker.
    def exitDictorsetmaker(self, ctx:Python3Parser.DictorsetmakerContext):
        atom_name_terminals.convert_dictorsetmaker(self, ctx)
