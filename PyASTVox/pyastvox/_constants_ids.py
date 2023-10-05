'''
This file defines additional speech generation functions for the class
pyastvox_speech_generator.  This file contains the functions for constants and
IDs.
'''

import ast

class constants_ids_mixin:
  def gen_ast_Constant(self, node):
    '''
    Generate speech for ast.Constant.
    Just use the string, i.e., str(), of the constant as the speech 
    '''
    node.jvox_speech = {"default": str(node.value)}
    #node.jvox_data = ast.dump(node)
    return

  def similar_to_keywords(self, name:str):

    if name.lower() == "true":
      is_similar = True
    elif name.lower() == "False":
      is_similar = True
    else:
      is_similar = False
    
    return is_similar
    
  def gen_ast_Name(self, node):
    '''
    Generate speech for ast.Name, i.e., a variable.
    Just use the variable name/identifier as the speech.
    '''
    if node.id == 'a' or node.id == "A":
      # append "-" so that gTTs won't read it as an article
      speech = node.id + "-"
    elif self.similar_to_keywords(node.id):
      speech = f"\"variable\" {node.id}"
    else:
      speech = node.id
      
    node.jvox_speech = {"default": speech}
    return
