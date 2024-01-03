'''
This file defines additional speech generation functions for the class
pyastvox_speech_generator.  This file contains the functions for constants and
IDs.
'''

import ast

class constants_ids_mixin:
  # special processing for variable name for better screen reading
  # e.g., to avoid "a" being read as an article, convert "a" to a-"
  def var_name_special_processing(self, var_name):
    if var_name == 'a' or var_name == "A":
      # append "-" so that gTTs won't read it as an article
      speech = var_name + "-"
    elif self.similar_to_keywords(var_name):
      speech = f"\"variable\" {var_name}"
    else:
      speech = var_name

    return speech

  
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
    # if node.id == 'a' or node.id == "A":
    #   # append "-" so that gTTs won't read it as an article
    #   speech = node.id + "-"
    # elif self.similar_to_keywords(node.id):
    #   speech = f"\"variable\" {node.id}"
    # else:
    #   speech = node.id
    speech = self.var_name_special_processing(node.id)
      
    node.jvox_speech = {"default": speech}
    return
