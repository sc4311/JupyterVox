# 1. Terminal Tokens
## 1.1 NUMBER
1. Integer string => ast.Constant(value:int)
2. Float string => ast.Constant(value:float)

# 2. Non-terminal Tokens
## 2.1 name
### 2.1.1 name: NAME
1. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
### 2.1.2 name: '_'
1. Not sure if this is right
2. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
### 2.1.2 name: 'match'
1. Not sure if this is right
2. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
## 2.2 atom
### 2.2.1 atom: name
1. AtomContext.pyast_tree <= AtomContext.children[0].pyast_tree (copy child)
### 2.2.2 atom: NUMBER
1. AtomContext.pyast_tree <= ast.Constant(AtomContext.children[0]), see 1.1 NUMBER
### 2.2.3 atom:STRING+
1. AtomContext.pyast_tree <= ast.Constant
    1. value <= concatenated string tokens
    2. A separate list "original_strings" is also added to the ast.Constant node with individual strings in STRING+
    3. String is processes to remove leading and trailing " and '
### 2.2.3 atom:"True" | "False"
1. AtomContext.pyast_tree <= ast.Constant
    1. value <= True or False, based on the actual statement text
### 2.2.x Other not implemented yet

## 2.3 atom_expr
### 2.3.1 atom_expr: AWAIT? atom trailer*
1. atom_expr.pyast_tree <= atom_expr.children[0].pyast_tree (copy child)
2. basically rule: atom_expr: atom
3. AWAIT? and trailer* not handled yet

## 2.4 expr
### 2.4.1 expr; atom_expr
1. exprContext.pyast_tree <= exprContext.children[0].pyast_tree (copy child)
### 2.4.2 expr: expr binaryOp expr
1. ExprContext.pyast_tree <= ast.BinOp(left expr, ast.Add/ast.Mult etc., right expr)
2. Covers
> Expr:   | expr '**' expr <br/>
>    | expr ('*'|'@'|'/'|'%'|'//') expr <br/>
>    | expr ('+'|'-') expr <br/>
>    | expr ('<<' | '>>') expr <br/>
>    | expr '&' expr <br/>
>    | expr '^' expr <br/>
>    | expr '|' expr <br/>
### 2.4.3 expr: ('+'|'-'|'~')+ expr, i.e., UnaryOp 
1. ExprContext.pyast_tree <= ast.UnaryOp(ast.UAdd/USub/Invert*, right epxr)
2. \* means nested tree

## 2.5 expr_stmt:
### 2.5.1 expr_stmt: testlist_star_expr
1. Epxr_stmtContext.pyast_tree <= ast.Expr(Epxr_stmtContext.children[0].pyast_tree)
### 2.5.x Other parts of the rule not handled
Full rule:<br/>
expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
                     ('=' (yield_expr|testlist_star_expr))*);

## 2.6 simple_stmts
### 2.6.1 simple_stmts: simple_stmt (';' simple_stmt)* ';'? NEWLINE;
1. Simple_stmtsContext.pyast_tree = [Simple_stmtsContext.children[*].pyast_tree]
2. The tree is a list containing the trees of all simple_stmt children 
3. ';' and NEWLINE are omitted from the list

## 2.7 single_input
### 2.7.1 single_input: NEWLINE
1. single_inputContext.pyast_tree <= ast.Module(body=[]) (empty list for body)
### 2.7.2 single_input: simple_stmts
1. single_inputContext.pyast_tree <= ast.Module(body=single_inputContext.Children[0].pyast_tree)
### 2.7.3 single_input: compound_stmt NEWLINE;
1. single_inputContext.pyast_tree <= ast.Module(body=single_inputContext.Children[0].pyast_tree)

## 2.8 flow_stmt
### 2.8.1 flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt;
1. Flow_stmtContext.pyast_tree <= Flow_stmtContext.children[0].pyast_tree (child copy)
2. Flow_stmt is just a intermediate non-terminal

## 2.9 return_stmt
### 2.9.1 return_stmt: 'return' testlist?;
1. Return_stmtContext.pyast_tree <= ast.Return
2. for ast.Return.value
    1. if no return value, value <= None
    2. if return on value, value <= Return_stmtContext.children[1]
    3. if return a list of values, value <= ast.Tuple
         1. ast.Tuple.elts <= Return_stmtContext.children[1]
         2. basically copy testlist's pyast_tree, which is a list

## 2.10 testlist
### 2.10.1 testlist: test (',' test)* ','?;
1. If there is just one child
    1.  TestlistContext.pyast_tree <= TestlistContext.children[0].pyast_tree (copy_child)
2. If there are more than one child
    1. TestlistContext.pyast_tree <= [] (just a list)
    2. the pyast_tree of each child of testlistContext is an item in the list

## 2.11 block
### 2.11.1 block: simple_stmts
1. BlockContext.pyast_tree <= BlockContext.children[0].pyast_tree (copy_child)
### 2.11.2 block: NEWLINE INDENT stmt+ DEDENT;
1. BlockContext.pyast_tree = []
2. Each item is the pyast_tree of a stmt
### 2.11.3 block: epsilon | NEWLINE epsilon
1. BlockContext.pyast_tree = None
2. This is a special error case, where the block is none. This should only happen when we are parsing on the first line of a compound statment, e.g., the "for ..." line of a for loop
    1. block: epsilon is for cases like "for i in j:"
    2. block: NEWLINE epsilon is for cases like "for i in j:\n"

## 2.12 for
### 2.12.1 for_stmt: 'for' exprlist 'in' testlist ':' block ('else' ':' block)?;
1. ForContext.pyast_tree <= ast.For
    1. target:
        1. If exprlist has only one child, target <= exprlist.pyast_tree, convert ctx to ast.Store
        2. If exprlist has more children, target <= ast.Tuple(elts=exprlist.pyast_tree)
    2. iter:
        1. If testlist has only one child, iter <= testlist.pyast_tree, 
        2. If testlist has more children, iter <= ast.Tuple(elts=testlist.pyast_tree)  
    3. body:
        1. If block has only one child, body <= [block.pyast_tree] (one item list) 
        2. If block has more children, body <= block.pyast_tree (list of stmts)
### 2.12.2 Grammar from 'else' is not handled yet

## 2.13 exprlist
### 2.13.1 exprlist: (expr|star_expr) (',' (expr|star_expr))* ','?;   
1. If there is just one child
    1.  ExprlistContext.pyast_tree <= ExprlistContext.children[0].pyast_tree (copy child)
2. If there are more than one child
    1. ExprlistContext.pyast_tree <= [] (just a list)
    2. the pyast_tree of each child of ExprlistContext is an item in the list

## 2.14 compound_stmt
### 2.14.1  compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt | match_stmt;
1. Compound_stmtContext.pyast_tree <= Compound_stmtContext.children[0].pyast_tree (copy_child)   

## 2.15 comp_op
### 2.15.1 comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not';
1. Comp_opContext.pyast_tree <= ast.Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn, based on the actual operator

## 2.16 while_stmt
### 2.16.1  while_stmt: 'while' test ':' block ('else' ':' block)?;
1. While_stmtContext.pyast_tree <= ast.While
    1. test: While_stmtContext.children[1].pyast_tree
    2. body: 
        1. If block has only one child, body <= [block.pyast_tree] (one item list) 
        2. If block has more children, body <= block.pyast_tree (list of stmts)
    3. orelse:
        1. If the second block has only one child, orelse <= [block.pyast_tree] (one item list) 
        2. If the second block has more children, orelse <= block.pyast_tree (list of stmts)
        3. If no "else", orelse <= [] (empty list)

## 2.17 comparison
### 2.15.1 comparison: expr (comp_op expr)*;
1. if only one expr, ComparisonContext.pyast_tree <= ComparisonContext.children[0].pyast_tree (copy child)
2. if more than one child
    1. ComparisonContext.pyast_tree <= ast.Compare
        1. left <= first epxr's pyast_tree
        2. ops <= [all comp_ops' pyast_tree] (list of comp_ops' pyast_tree)
        3. comparators <= [all the rest exprs' pyast_tree] (list of the rest exprs' pyast_tree)

## 2.18 if_stmt
### 2.18.1 if_stmt: 'if' test ':' block ('elif' test ':' block)* ('else' ':' block)?;
1. If_stmtContext.pyast_tree <= ast.If
    1. test = If_stmtContext.children[1].pyast_tree
    2. body = If_stmtContext.children[1].pyast_treee
    3. orelse
        1. if no elif or else, orelse <= [] (empty list)
        2. if elif, orelse <= ast.If (elif is nested, ie, next elif's node is stored in this elif's orelse)
            1. test = If_stmtContext.children[5].pyast_tree
            2. body = If_stmtContext.children[7].pyast_tree
            3. orelse, same with the above else. Again, elif is nested, ie, next elif's node is stored in this elif's orelse
        3. if "else", orelse = last_block.pyast_tree

## 2.19 stmt
### 2.14.1  stmt: simple_stmts | compound_stmt;
1. StmtContext.pyast_tree <= StmtContext.children[0].pyast_tree (copy_child)   
