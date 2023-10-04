# Style Guide

## ast.Constant
1. default: the str() conversion of the constant's value
## ast.Name
1. default: the id of the variable (ast.Name node)
## ast.Add
1. direct: "plus"
2. indirect: "the sum of"
## ast.Mult
1. direct: "multiply"
2. indirect: "the product of"
## ast.Sub
1. direct: "minus"
2. indirect: "the difference of"
## ast.Div
1. direct: "divide"
## ast.Mod
1. direct: "modulo"
## ast.FloorDiv
1. direct: "floor divide"
## ast.MatMult
1. direct: "matrix multiply"
## ast.Pow
1. direct: "to the power of"
## ast.USub
1. direct: "negative"
## ast.BinOp
1. default: "left op.direct right", 
   1. e.g., "a+b*c", a plus b multiply c
   2. e.g., "(a+b)*c", a plus b, then multiply c
2. indirect: "the sum/product/difference... of left and right"
   1. e.g., "a+b*c", the sum of a and the sum of b and c
   2. e.g., "(a+b)*c", the product of the sum of a and b, and c
2. alternate: alternating default and indirect styles for each level of expressions
   1. e.g., "a+b*c", a plus the product of b and c
   2. e.g., "(a+b)*c", the sum of a plus b, then multiply c
   3. jvox_data is used to hold if the speech is direct or indirect
   4. lowest level is indirect
