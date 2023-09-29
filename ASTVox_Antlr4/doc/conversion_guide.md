# 1. Terminal Tokens
## 1.1 NUMBER
1. Integer string => ast.Constant(value:int)
2. Float string => ast.Constant(value:float)

# 2. Non-terminal Tokens

## 2.0 General Guidelines
### 2.0.1 List type of tokens
1. List type of tokens are those drived from one or two repeated items, e.g., simple_stmts: simple_stmt (';' simple_stmt)* ';'? NEWLINE;
2. Should always return a list as the pyast_tree
3. This may not hold for all list-typed tokens, if they are implemented before 09/15/2023
### 2.0.2 Load/Store contexts
1. ctx is defaulted to ast.Load()
2. all ctx in a subtree will be changed if that tree is determined to be written (e.g., left hand of an assignment statement)

## 2.1 name
### 2.1.1 name: NAME
1. name.pyast_tree <= ast.Name, fields are
    1. id = NAME.getText(), 
    2. ast.Load())
### 2.1.2 name: '_'
1. Not sure if this is right
2. name.pyast_tree <= ast.Name, fields are
    1. id = NAME.getText(), 
    2. ast.Load())
### 2.1.2 name: 'match'
1. Not sure if this is right
2. name.pyast_tree <= ast.Name, fields are
    1. id = NAME.getText(), 
    2. ast.Load())
    
## 2.2 atom
### 2.2.1 atom: name
1. atom.pyast_tree <= name.pyast_tree (copy child)
### 2.2.2 atom: NUMBER
1. atom.pyast_tree <= ast.Constant(NUMBER), see 1.1 NUMBER
### 2.2.3 atom:STRING+
1. atom.pyast_tree <= ast.Constant, fields are,
    1. value <= concatenated string tokens
    2. A separate list "original_strings" is also added to the ast.Constant node with individual strings in STRING+
    3. String is processes to remove leading and trailing " and '
### 2.2.3 atom: "True" | "False"
1. atom.pyast_tree <= ast.Constant, fields are,
    1. value <= True or False, based on the actual statement text
### 2.2.4 atom: '(' (testlist_comp)? ')'
1. If there is no testlist_com
    1. atom.pyast_tree <= ast.Tuple, fields are,
        1. elts = [] (empty list)
        2. ctx = ast.Load()
2. If there is one item in testlist_comp, 
    1. atom.pyast_tree <= testlist_comp.pyast_tree (copy child)
3. If there are more than one items in testlis_comp,
    1. atom.pyast_tree <= ast.Tuple, fields are,
        1. elts <= testlist_comp.pyast_tree
        2. ctx = ast.Load()
4. if testlist_comp.pyast_treeis not a list but a dict, 
    1. testlist_comp is derived with rule, "testlist_comp: test comp_for." This is a comprehension.
    2. atom.pyast_tree <= ast.GeneratorExp, fields are,
        1. elt = testlist_comp.pyast_tree["elt"]
        2. generators = elt = testlist_comp.pyast_tree["generators"]
### 2.2.4 atom: '[' testlist_comp? ']'
1. If there is no testlist_com
    1. atom.pyast_tree <= ast.List, fields are,
        1. elts = [] (empty list)
        2. ctx = ast.Load()
2. If testlist_comp.pyast_tree is a list, 
    1. atom.pyast_tree <= ast.List, fields are,
        1. elts = testlist_comp.pyast_tree (copy ist)
        2. ctx = ast.Load()
4. if testlist_comp.pyast_tree is not a list but a dict, 
    1. testlist_comp is derived with rule, "testlist_comp: test comp_for." This is a comprehension.
    2. atom.pyast_tree <= ast.ListComp, fields are,
        1. elt = testlist_comp.pyast_tree["elt"]
        2. generators = elt = testlist_comp.pyast_tree["generators"]
### 2.2.4 atom: '{' dictorsetmaker? '}'
1. There is no dictorsetmaker
    1. atom.pyast_tree = ast.Dict, fields,
        1. keys = [] (empty list)
        2. values = [] (empty list)
2. If there is dictorsetmaker, 
    1. atom.pyast_tree = dictorsetmaker.pyast_tree (copy child)
    2. ast.Dict/ast.DictComp/ast.Set/ast.SetComp is generated in dictorsetmaker
### 2.2.x Other not implemented yet

## 2.3 atom_expr
1. the real grammar is atom_expr: AWAIT? atom trailer*
2. the process is a bit complext, so I wills with basic cases, that there is no AWAIT, and only atom or only atom trailer 
### 2.3.1 atom_expr: atom
1. atom_expr.pyast_tree <= atom_expr.children[0].pyast_tree (copy child)
2. basically rule: atom_expr: atom
3. AWAIT? and trailer* not handled yet
### 2.3.2 atom_expr: atom '(' arglist ')'
1. That is, trailer is '(' arglist ')'
2. atom_expr.pyast_tree <= ast.Call, fields are, 
    1. func = atom.pyast_tree
    2. keywards: [...] 
        1. any ast.keyword items in arglist.pyast_tree (which is a list)
    3. args: [...]
        1. any other typed (i.e., ast.keyword) items in arglist.pyast_tree (which is a list)
### 2.3.3 atom_expr: atom '[' subscriptionlist ']'
1. That is, trailer is '[' subscriptionlist ']'
2. atom_expr.pyast_tree <= ast.Subscript, fields are, 
    1. value = atom.pyast_tree
    2. slice_field: 
        1. if subscriptionlist.pyast_tree has only one item, subscriptionlist.pyast_tree[0], 
        2. if subscriptionlist.pyast_tree has more than one item2, ast.Tuple, fields are,
            1. elts <= subscriptionlist.pyast_tree             
### 2.3.4 atom_expr: atom '.' name
1. That is, trailer is '.' name
2. atom_expr.pyast_tree <= ast.Attribute, fields are, 
    1. value <= atom.Attribute
    2. attr <= name.getText() 
### 2.3.5 atom_expr: atom trailer+
1. recursively build the tree
2. First atom trailer at the *lowest* level.
3. Then the rest trailer gradually increase from the lowest level.
4. E.g., atom trailer1 trailer2 trailer3 has the ast node for trailer3 at the top level, trailer2 at the 2nd level, atom trailer1 at the lowest level.
5. E.g., for a()[1].c, the nodes order are (from top to bottom) ast.attribute => ast.Subscript=>ast.Call
### 2.3.6 atom_expr: AWAIT atom trailer*
1. atom_expr.pyast_tree <= ast.AWAIT, fields are,
    1. value = the Python AST tree converted from "atom trailer*)


## 2.4 expr
### 2.4.1 expr; atom_expr
1. expr.pyast_tree <= atom_expr.pyast_tree (copy child)
### 2.4.2 expr: expr1 binaryOp expr2
1. expr.pyast_tree <= ast.BinOp, fields are 
    1. left = expr1.pyast_tree, 
    2. op = ast.Add() or ast.Mult(), based on the binaryOp's text 
    3. right = expr2.pyast_tree
2. Covers
> Expr:   | expr '**' expr <br/>
>    | expr ('*'|'@'|'/'|'%'|'//') expr <br/>
>    | expr ('+'|'-') expr <br/>
>    | expr ('<<' | '>>') expr <br/>
>    | expr '&' expr <br/>
>    | expr '^' expr <br/>
>    | expr '|' expr <br/>
### 2.4.3 expr: ('+'|'-'|'~')+ expr, i.e., UnaryOp 
1. expr.pyast_tree <= ast.UnaryOp, fields are,
    1. op = ast.UAdd()/USub()/Invert*, 
    2. operand = epxr.pyast_tree
2. \* means nested tree

## 2.5 expr_stmt:
### 2.5.1 expr_stmt: testlist_star_expr
1. expr_stmt.pyast_tree <= ast.Expr(testlist_star_expr.pyast_tree)
### 2.5.2 expr_stmt : testlist_star_expr '=' testlist_star_expr
1. expr_stmt.pyast_tree <= ast.Assign
    1. targets <= [the pyast_tree of every testlist_star_expr except the last one]
    2. value <= the last testlist_star_expr's pyast_tree
### 2.5.x Other parts of the rule not handled
Full rule:<br/>
expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
                     ('=' (yield_expr|testlist_star_expr))*);

## 2.6 simple_stmts
### 2.6.1 simple_stmts: simple_stmt (';' simple_stmt)* ';'? NEWLINE;
1. simple_stmts.pyast_tree = [the pyast_tree of each simple_stmt]
2. The tree is a list containing the trees of all simple_stmt children 
3. ';' and NEWLINE are omitted from the list

## 2.7 single_input
### 2.7.1 single_input: NEWLINE
1. single_input.pyast_tree <= ast.Module(body=[]) (empty list for body)
### 2.7.2 single_input: simple_stmts
1. single_input.pyast_tree <= ast.Module(body=simple_stmts].pyast_tree)
### 2.7.3 single_input: compound_stmt NEWLINE;
1. single_input.pyast_tree <= ast.Module(body=compound_stmt.pyast_tree)

## 2.8 flow_stmt
### 2.8.1 flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt;
1. flow_stmt.pyast_tree <= Flow_stmtContext.children[0].pyast_tree (child copy)
2. flow_stmt is just a intermediate non-terminal

## 2.9 return_stmt
### 2.9.1 return_stmt: 'return' testlist?;
1. return_stmt.pyast_tree <= ast.Return
2. for ast.Return.value,
    1. if no return value, value <= None
    2. if return on value, value <= Return_stmtContext.children[1]
    3. if return a list of values, value <= ast.Tuple
         1. ast.Tuple.elts <= Return_stmtContext.children[1]
         2. basically copy testlist's pyast_tree, which is a list

## 2.10 testlist
### 2.10.1 testlist: test (',' test)* ','?;
1. testlist.pyast_tree <= [...] (just a list)
2. the pyast_tree of each child of testlistContext is an item in the list

## 2.11 block
### 2.11.1 block: simple_stmts
1. block.pyast_tree <= BlockContext.children[0].pyast_tree (copy_child)
### 2.11.2 block: NEWLINE INDENT stmt+ DEDENT;
1. block.pyast_tree = []
2. Each item is the pyast_tree of a stmt
### 2.11.3 block: epsilon | NEWLINE epsilon
1. block.pyast_tree = None
2. This is a special error case, where the block is none. This should only happen when we are parsing on the first line of a compound statment, e.g., the "for ..." line of a for loop
    1. block: epsilon is for cases like "for i in j:"
    2. block: NEWLINE epsilon is for cases like "for i in j:\n"

## 2.12 for
### 2.12.1 for_stmt: 'for' exprlist 'in' testlist ':' block ('else' ':' block)?;
1. for_stmt.pyast_tree <= ast.For, fields are,
    1. target:
        1. If exprlist has only one child, target <= exprlist.pyast_tree, convert ctx to ast.Store
        2. If exprlist has more children, target <= ast.Tuple(elts=exprlist.pyast_tree)
    2. iter:
        1. If testlist has only one child, iter <= testlist.pyast_tree, 
        2. If testlist has more children, iter <= ast.Tuple(elts=testlist.pyast_tree)  
    3. body:
        1. If block has only one child, body <= [block.pyast_tree] (one item list) 
        2. If block has more children, body <= block.pyast_tree (list of stmts)
    3. orelse:
        1. If the second block has only one child, orelse <= [block.pyast_tree] (one item list) 
        2. If the second block has more children, orelse <= block.pyast_tree (list of stmts)
        3. If no "else", orelse <= [] (empty list)
        
## 2.13 exprlist
### 2.13.1 exprlist: (expr|star_expr) (',' (expr|star_expr))* ','?;   
1. exprlist.pyast_tree <= [...] (just a list)
2. the pyast_tree of each child of ExprlistContext is an item in the list

## 2.14 compound_stmt
### 2.14.1  compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt | match_stmt;
1. compound_stmt.pyast_tree <= Compound_stmtContext.children[0].pyast_tree (copy_child)   

## 2.15 comp_op
### 2.15.1 comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not';
1. comp_op.pyast_tree <= ast.Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn, based on the actual operator

## 2.16 while_stmt
### 2.16.1  while_stmt: 'while' test ':' block ('else' ':' block)?;
1. while_stmt.pyast_tree <= ast.While, fields are,
    1. test: test.pyast_tree
    2. body: 
        1. If block has only one child, body <= [block.pyast_tree] (one item list) 
        2. If block has more children, body <= block.pyast_tree (list of stmts)
    3. orelse:
        1. If the second block has only one child, orelse <= [block.pyast_tree] (one item list) 
        2. If the second block has more children, orelse <= block.pyast_tree (list of stmts)
        3. If no "else", orelse <= [] (empty list)

## 2.17 comparison
### 2.15.1 comparison: expr (comp_op expr)*;
1. if only one expr, comparison.pyast_tree <= ComparisonContext.children[0].pyast_tree (copy child)
2. if more than one child
    1. ComparisonContext.pyast_tree <= ast.Compare, fields are,
        1. left <= first epxr's pyast_tree
        2. ops <= [all comp_ops' pyast_tree] (list of comp_ops' pyast_tree)
        3. comparators <= [all the rest exprs' pyast_tree] (list of the rest exprs' pyast_tree)

## 2.18 if_stmt
### 2.18.1 if_stmt: 'if' test ':' block ('elif' test ':' block)* ('else' ':' block)?;
1. if_stmt.pyast_tree <= ast.If, fields are,
    1. test = If_stmtContext.children[1].pyast_tree
    2. body 
        1. If block (If_stmtContext.children[1]) has only one child, body <= [block.pyast_tree] (one item list) 
        2. If block (If_stmtContext.children[1]) has more children, body <= block.pyast_tree (list of stmts)
    3. orelse
        1. if no elif or else, orelse <= [] (empty list)
        2. if elif, orelse <= ast.If (elif is nested, ie, next elif's node is stored in this elif's orelse)
            1. test = If_stmtContext.children[5].pyast_tree
            2. body = If_stmtContext.children[7].pyast_tree
            3. orelse, same with the above else. Again, elif is nested, ie, next elif's node is stored in this elif's orelse
        3. if "else", 
            1. If last block has only one child, body <= [block.pyast_tree] (one item list) 
            2. If last block has more children, body <= block.pyast_tree (list of stmts)

## 2.19 stmt
### 2.14.1  stmt: simple_stmts | compound_stmt;
1. stmt.pyast_tree <= simple_stmts.pyast_tree or compound_stmt.pyast_tree (copy_child) 

## 2.20 star_expr
### 2.20.1  star_expr: '*' expr;
1. star_expr.pyast_tree <= ast.Starred, fields are,
    1. value = Star_exprContext.children[1].pyast_tree (expr's ast node)

## 2.21 testlist_star_expr
### 2.21.1 testlist_star_expr: (test|star_expr) (',' (test|star_expr))* ','?;
1. testlist_star_expr.pyast_tree <= [..] (a list)
2. Each test or star_expr child's pyast_tree is a item in the list

## 2.22 testlist_comp
### 2.22.1 testlist_comp: (test|star_expr) ( (',' (test|star_expr))* ','? );
1. testlist_comp.pyast_tree <= [..] (a list)
2. Each test or star_expr child's pyast_tree is a item in the list 
### 2.22.2 testlist_comp: (test|star_expr) comp_for
1. testlist_comp.pyast_tree = {"elt": ..., "generators":[...]}
    1. elt = test.pyast_tree or star_expr.pyast_tree
    2. generators = comp_for.pyast_tree["comprehensions"]

## 2.22 dictorsetmaker
### 2.22.1 dictorsetmaker: (test ':' test | '**' expr) (',' (test ':' test | '**' expr))* ','?)
1. For making a dictonary
2. dictorsetmaker.pyast_tree <= ast.Dict, fields are,
    1. keys = [...], items are
        1. for each "** expr", None
        2. for each "test" before ":", test.pyast_tree
    2. values = [...], items are
        1. for each "** expr", expr.pyast_tree
        2. for each "test" after ":", test.pyast_tree
### 2.22.2 dictorsetmaker: test1 ':' test2 comp_for
1. For making a dictonary with comprehension
2. dictorsetmaker.pyast_tree <= ast.DictComp, fields are,
    1. key = test1.pyast_tree
    2. value = test2.pyast_tree
    3. generators = comp_for.pyast_tree["comprehensions"]
### 2.22.3 dictorsetmaker: **expr comp_for
1. ** NOT HANDLE **
2. This is valid for Antlr4's grammar, but not real Python
### 2.22.4 dictorsetmaker: (test | star_expr) (',' (test | star_expr))* ','?)
1. For making a set
2. dictorsetmaker.pyast_tree <= ast.Set, fields are,
    1. values = [...], items are
        1. for each "** expr", expr.pyast_tree
        2. for each "test", test.pyast_tree
### 2.22.5 dictorsetmaker: (test | star_expr) comp_for
1. For making a set with comprehension
2. dictorsetmaker.pyast_tree <= ast.SetComp, fields are,
    1. elt = test.pyast_tree, or star_expr.pyast_tree
    2. generators = comp_for.pyast_tree["comprehensions"]


## 2.23 not_test
### 2.23.1 not_test: comparison
1. Or_testContext.pyast_tree <= Or_testContext.children[0].pyast_tree (copy_child) 
### 2.23.2 not_test: 'not' not_test
1. Or_testContext.pyast_tree <= ast.UnaryOp(), fields are,
    1. op <= ast.Not()
    2. operand <= Or_testContext.children[1].pyast_tree

## 2.24 and_test
### 2.24.1 and_test: not_test
1. And_testContext.pyast_tree <= And_testContext.children[0].pyast_tree (copy_child) 
### 2.24.2 and_test: not_test ('and' not_test)+
1. And_testContext.pyast_tree <= ast.BoolOp(), fields are,
    1. op <= ast.And()
    2. values <= [the pyast_tree of all no_test children] (a list)

## 2.25 or_test
### 2.25.1 or_test: and_test
1. Or_testContext.pyast_tree <= Or_testContext.children[0].pyast_tree (copy_child) 
### 2.25.2 or_test: and_test ('or' and_test)+
1. Or_testContext.pyast_tree <= ast.BoolOp(), fields are,
    1. op <= ast.Or()
    2. values <= [the pyast_tree of all and_test children] (a list)

## 2.26 test
### 2.26.1 test: or_test | lambdef;
1. TestContext.pyast_tree <= TestContext.children[0].pyast_tree (copy_child) 
### 2.26.2 test: or_test ('if' or_test 'else' test)
1. Or_testContext.pyast_tree <= ast.IfExp(), fields are,
    1. body <= TestContext.children[0].pyast_tree
    2. test <= TestContext.children[2].pyast_tree
    3. orelse <= TestContext.children[4].pyast_tree

## 2.27 tfpdef
### 2.27.1 tfpdef: name (':' test)?;
1. TfpdefContext.pyast_tree <= ast.arg, fields are,
    1. arg: TfpdefContext.children[0].getText()
    2. annotation: TfpdefContext.children[2].pyast_tree

## 2.28 typedargslist
### 2.28.1 typedargslist: (tfpdef ('=' test)? (',' tfpdef ('=' test)?)* (',' ('*' tfpdef? (',' tfpdef ('=' test)?)* (',' ('**' tfpdef ','? )? )? | '**' tfpdef ','? )? )? | '*' tfpdef? (',' tfpdef ('=' test)?)* (',' ('**' tfpdef ','? )? )? | '**' tfpdef ','?);
1. This grammar is super complex. But there are basically four cases:
    1. normal args + *vararg + kwonly args + **kwarg
    2. normal args + **kwarg
    3. *kwarg + kwonly args + **kwarg
    4. **kwarg
2. TypedargslistContext.pyast_tree = ast.arguments(), fields are,
    1. posonlyargs == [] (empty list, Antlr4 grammar does not handle it at the moment)
    2. args = [...], defaults = [...], for normal arguments
        1. normal args are: (tfpdef ('=' test)? (',' tfpdef ('=' test)?)*
        2. all pyast_trees of tfpdef's go into the args list
        3. all pyast_trees of test's go into the default list
        4. if no normal args, both lists are empty
    3. vararg
        1. vararg is: '*' tfpdef
        2. vararg <= tfpdef.pyast_tree, should be an ast.arg typed object
        3. None, if vararg does not exist
    4. kwonlyargs = [...], kw_defaults =[...], for keyword-only variables
        1. kwonly args are: (tfpdef ('=' test)? (',' tfpdef ('=' test)?)*, that are defined after *vararg
        2. all pyast_trees of tfpdef's go into the kwonlyargs list
        3. all pyast_trees of test's go into the kw_defaults list
        4. if a keyword only argumetn does not have default value, None is used for the kw_defaults list
        4. if no keyword-only args, both lists are empty
    5. kwarg
        1. kwarg is: '**' tfpdef
        2. kwarg <= tfpdef.pyast_tree, should be an ast.arg typed object
        3. None, if kwarg does not exist
    
## 2.29 parameters
### 2.29.1 parameters: '(' typedargslist? ')';
1. ParametersContext.pyast_tree <= ParametersContext.children[1].pyast_tree (copy_child) 

## 2.30 funcdef
### 2.30.1 funcdef: 'def' name parameters ':' block;
1. FuncdefContext.pyast_tree <= ast.FuncdefContext, fields are,
    1. name: FuncdefContext.children[1].getText()
    2. args: FuncdefContext.children[2].pyast_tree
    3. body: FuncdefContext.children[4].pyast_tree 
    4. decorator_list: [] empty list, not sure how to handle this
    5. returns <= None
### 2.30.2 funcdef: 'def' name parameters ('->' test)? ':' block;
1. FuncdefContext.pyast_tree <= ast.FuncdefContext, fields are,
    1. name: FuncdefContext.children[1].getText()
    2. args: FuncdefContext.children[2].pyast_tree
    3. body: FuncdefContext.children[6].pyast_tree 
    4. decorator_list: [] empty list, not sure how to handle this
    5. returns: FuncdefContext.children[4].pyast_tree 
### 2.30.3 Bug:
Antlr4's grammar allows parameters of (a=1, b), but Python AST does not. i.e., "def  f(a=1,b):return" will fail with Python AST.

## 2.31 test_nocond
### 2.31.1 test_nocond: or_test | lambdef_nocond;
1. Test_nocondContext.pyast_tree <= Test_nocondContext.children[1].pyast_tree (copy_child) 

## 2.32 comp_if
### 2.32.1 comp_if: 'if' test_nocond comp_iter?;
1. comp_ifContext.pyast_tree <= {"ifs":[...], "comprehensions":[...]}
    1. Intuitively, the "comprenhensions" list includes the comprehensions in the "generators" field of an ast.ListComp/SetComp/GeneratorExp/DictComp list. This "comprenhensions" list is inherited from the list of comp_iter. i.e.,
        1. "comprehensions":[...] <= comp_iter.pyast_tree["comprehensions"]
        2. if not comp_iter, "comprehensions" is an empty list [].
    2. The "ifs":[...] includes the "if" statements from children comp_if tokens, which will be used by an upper-level comp_for node as the "ifs" field of and ast.comprehension node.
        1. a new item (denoted as new_if) for "ifs" list is copied from test_nocond.pyast_tree
        2. if no comp_iter, "ifs" is a just [new_if] 
        3. if there is comp_iter, "ifs" is [new_if] + comp_iter.pyast_tree["ifs"]. Note new_if is at the beginning of the new list.

## 2.33 comp_for
### 2.33.1 comp_for: ASYNC? 'for' exprlist 'in' or_test comp_iter?;
1. comp_forContext.pyast_tree <= {"ifs":[], "comprehensions":[...]}
    1. "ifs" is always an empty list.
        1. If there are "ifs" from comp_iters, they are used to construct the ast.comprehension node (see blow).
    2. comp_for creates a new ast.comprehension node (denoted as new_comp). The fields of new_comp are,
        1. target <= exprlist.pyast_tree
        2. iter <= or_test.pyast_tree
        3. ifs <= comp_iter.pyast_tree["ifs"] if comp_iter exists; otherwise, ifs<=[] (empty list)
        4. is_async <= 1 if ASYNC is there, 0 if no ASYNC
    3. if no comp_iter, "comprehensions" is a just [new_comp] 
    4. if there is comp_iter, "comprehensions" is [new_comp] + comp_iter.pyast_tree["comprehensions"]. Note new_if is at the beginning of the new list.


## 2.34 comp_iter
### 2.34.1 comp_iter: comp_for | comp_if
1. Comp_iterContext.pyast_tree <= Comp_iterContext.children[0].pyast_tree (copy_child) 
2. Note that both comp_for and comp_if are translated into a dict with two lists, i.e., {"ifs":[...], "comprehensions":[...]}. Hence, comp_iter also returns these two lists.
    * Intuitively, the "comprenhensions" list includes the comprehensions in the "generators" field of an ast.ListComp/SetComp/GeneratorExp/DictComp list.
    * The "ifs":[...] includes the "if" statements from children comp_if tokens, which will be used by an upper-level comp_for node as the "ifs" field of and ast.comprehension node.
    * The problem with comp_iter, comp_for and comp_if is that they are generated as a tree of nodes in ANTLR4, however, they are supposed to be one the same-level in Python AST and the actual code being parsed. So we have to copy the ifs and comprehensions lists from the children comp_iter/comp_for/comp_if nodes.

## 2.35 argument
## 2.35.1 argument: test 
1. ArgumentContext.pyast_tree <= ArgumentContext.children[0].pyast_tree (copy_child) 
## 2.35.2 argument: test comp_for
1. ArgumentContext.pyast_tree <= ast.GeneratorExp, fields are
    1. elt = ArgumentContext.children[0].pyast_tree
    2. generators = ArgumentContext.children[1].pyast_tree["comprehensions"]
## 2.35.3 argument: test '=' test
1. ArgumentContext.pyast_tree <= ast.keyword, fields are
    1. arg = ArgumentContext.children[0].getText()
    2. value = ArgumentContext.children[2].pyast_tree
## 2.35.4 argument: '**' test 
1. ArgumentContext.pyast_tree <= ast.keyword, fields are
    1. arg = None
    2. value = ArgumentContext.children[1].pyast_tree
## 2.35.5 argument: '*' test 
1. ArgumentContext.pyast_tree <= ast.Starred, fields are
    1. value <= ArgumentContext.children[1].pyast_tree
    2. ctx <= ast.Load()

## 2.36 arglist
### 2.36.1 arglist: argument (',' argument)* ','?;
1. ArglistContext.pyast_tree <= [..],
    1. each item in arglist is each argument.pyast_tree
    2. bascially return the lisf of arguments

## 2.37 classdef
### 2.37.1 classdef: 'class' name ('(' arglist? ')')? ':' block;
1. classdefContext.pyast_tree <= ast.ClassDef, fields are,
    1. name <= name.getText()
    2. body <= block.pyast_tree
    3. keywords: 
        1. any ast.keyword items in arglist.pyast_tree (which is a list)
    4. bases:
        1. any other typed (i.e., ast.keyword) items in arglist.pyast_tree (which is a list)
        2. there should be no ast.GeneratorExp nodes in arglist, due to Python syntax.
    5. decorator_list <= [] (empty list, decorators are parsed to higher level nodes in the AST tree)

## 2.38 trailer
### 2.38.1 trailer: '(' arglist? ')'
1. TrailerContext.pyast_tree <= {"type":"arglist", "values":[...]}
    1. type <="arglist" (a string)
    2. value <= the arglist.pyast_tree (which is a list)
### 2.38.2 trailer: trailer: '[' subscriptlist ']'
1. TrailerContext.pyast_tree <= {"type":"subscriptionlist", "values":[...]}
    1. type <= "subscriptionlist" (a string)
    2. value <= the subscriptlist.pyast_tree (which is a list)
### 2.38.3 trailer: '.' name
1. TrailerContext.pyast_tree <= {"type":"field", "values":[...]}
    1. type <= "field" (a string)
    2. value <= [name.pyast_tree]

## 2.39 sliceop
### 2.39.1 sliceop: ";";
1. SliceopContext.pyast_tree <= None
### 2.39.2 sliceop: ";" test;
1. SliceopContext.pyast_tree <= test.pyast_tree

## 2.40 subscript_
### 2.40.1 subscript_: test;
1. Subscript_Context.pyast_tree <= test.pyast_tree (copy_child) 
### 2.40.2 sliceop: test1? ':' test2? sliceop?;
1. Subscript_Context.pyast_tree <= ast.Slice, fields are
    1. lower: test1.pyast_tree if there is test1; otherwise, None
    2. upper: test2.pyast_tree if there is test2; otherwise, None
    3. step: slicop.pyast_tree if there is sliceop; otherwise, None


## 2.41 subscriptlist
### 2.41.1 subscriptlist: subscript_ (',' subscript_)* ','?;
1. SubscriptlistContext.pyast_tree <= [..],
    1. each item in arglist is each subscript_.pyast_tree
    2. bascially return the lisf of subscript_'s

## 2.42 dotted_as_name
### 2.42.1 dotted_as_name: dotted_name ('as' name)?;
1. Dotted_as_nameContext.pyast_tree <= ast.alias, fields
    1. name <= dotted_name.getText()
    2. asname 
        1. if has "as" name, asname <= name.getText() (three child)
        2. if no "as" name, asname <= None

## 2.43 dotted_as_names
### 2.43.1 dotted_as_names: dotted_as_name (',' dotted_as_name)*;
1. Dotted_as_namesContext <= [...] (a list)
    1. each item is one dotted_as_name. pyast_tree (should be an ast.alias node)

## 2.44 import_name
### 2.44.1 import_name: 'import' dotted_as_names;
1. Import_nameContext <= ast.Import, fields are,
    1. names = dotted_as_names.pyast_tree (a list of ast.alias nodeds)

## 2.45 import_stmt
### 2.45.1 import_stmt: import_name | import_from;
1. Import_stmtContext.pyast_tree <= Import_stmtContext.children[0].pyast_tree (copy child, either ast.Import or ast.ImportFrom)






