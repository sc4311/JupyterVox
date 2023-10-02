# This file defines additional member functions for the Class astparser, These
# functions parse the Python loops.

import ast

from speech import Speech

class loops_mixin:
    
    def emit_For(self, node, level):
        speech = Speech()

        # generate the speech for the loop variable and condition
        loop_var = self.emit(node.target)
        loop_cond = self.emit(node.iter)
        loop_cond_text = ""

        if (isinstance(node.iter, ast.Call) and
            node.iter.func.id == "range"): # "range" func as the iter
            loop_cond_text = ("for loop with loop variable " + loop_var.text +
                              " in " + loop_cond.text)
        elif isinstance(node.iter, ast.List): # a list as iter
            loop_cond_text = ("for loop with loop variable " + loop_var.text +
                              " in the " + loop_cond.text)
        elif isinstance(node.iter, ast.Name): # a variable as iter
            loop_cond_text = ("for loop with loop variable " + loop_var.text +
                              " in " + loop_cond.text)
        elif isinstance(node.iter, ast.Constant): # a constant as iter
            loop_cond_text = ("for loop with loop variable " + loop_var.text +
                              " in " + loop_cond.text)
        else:
            raise Exception("Unknown for loop iter: " + str(node.iter))

        # generate the speech for the loop body
        body_stmts = []
        for i in range(len(node.body)):
            b = self.emit(node.body[i])
            body_stmts.append(b.text)
        loop_body_text = ", ".join(body_stmts)

        # combine loop variable, condition and body
        speech.text = loop_cond_text + ", has a body of " + loop_body_text

        # if isinstance(s1, Speech) and isinstance(s2, Speech):
        #     if "ranging" in s2.text:
        #         speech.text = (f"for loop with condition {s1.text} "\
        #                        f"{s2.text}, has a body of {loop_body_text}")
        #     else:
        #         speech.text = (f"for loop with condition {s1.text} in "\
        #                        f"{s2.text}, has a body of {loop_body_text}")
        # elif isinstance(s1, Speech) and isinstance(s2, str):
        #     speech.text = (f"for loop with condition {s1.text} in {s2}, "\
        #                    f"has a body of {loop_body_text}")

        return speech
