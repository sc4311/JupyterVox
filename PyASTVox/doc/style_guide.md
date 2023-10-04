# General Notes
1. Each node has a jvox\_speech field after the speech generation routine. The
   jvox_speech is a dictionary with speeches for different styles. There should
   always be a "default" style. 
2. Jvox\_speech should also have a "selected\_style" to help the parent nodes to
   know which speech to use. If user selected a style, "selected\_style" will be
   using that style. Otherwise,  "default" is copied to "selected\_style." 
   This "selected\_style" is automatically selected by the
   set\_selected\_style\_speech\_for\_node function afer the speech is generated
   for each node (i.e., after gen_ast_XXX function is called)
   
# Per Node Style Guide
## ast.Constant
1. default: the str() conversion of the constant's value
## ast.Name
1. default: the id of the variable (ast.Name node)
2. Since "a/A"  is always read as the artical "a" than the letter "a/A" in gTTs,
   the speech of variable "a/A" is generated as "a-/A-".
## ast.Add
1. default: "plus"
2. indirect: "the sum of"
## ast.Mult
1. default: "multiply"
2. indirect: "the product of"
## ast.Sub
1. default: "minus"
2. indirect: "the difference of"
## ast.Div
1. default: "divide"
## ast.Mod
1. default: "modulo"
## ast.FloorDiv
1. default: "floor divide"
## ast.MatMult
1. default: "matrix multiply"
## ast.Pow
1. default: "to the power of"
## ast.USub
1. default: "negative"
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
