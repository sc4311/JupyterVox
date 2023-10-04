'''
Module pyastvox: JupyterVox screen reader based on the Python AST module.
'''

# Python packages
import ast

# Speech generation mixin classes, which have the actual implementation
# for gen_ast_XXX functions
import _alu_operations
import _constants_ids
import _unaryops

class pyastvox_speech_generator(_alu_operations.ops_mixin,
                                _constants_ids.constants_ids_mixin,
                                _unaryops.unaryops_mixin):
  '''
  Entry-point class for JupyterVox pyastvox module.
  Call the "generate" function with a Python AST tree node to generate the
  speech. The generated speech text (string) will be stored in the "jvox_speech"
  field of the tree node. Similarly, all descendants of this node will also have
  a 'jvox_speech" field to store their speech text.

  This class also has a "speech_styles" dictionary which controls the speech
  style for each type of ast nodes.
  '''
  # fields
  speech_styles: dict # speech styles for different type of nodes

  def __init__(self, speech_styles={}):
      self.speech_styles = speech_styles
      
      return

  def generate(self, node):
    '''
    Main entrance function to generate the speech for a tree
    Essentially depth first traversal: visit all desendents, generate speech for
    each of them.
    '''
    
    # visit all desendents, generate speech for each of them
    for field, value in ast.iter_fields(node):
      if isinstance(value, list):
        for item in value:
          if isinstance(item, ast.AST):
            self.generate(item)
      elif isinstance(value, ast.AST):
        self.generate(value)

    # generate speech for this level of node
    func = self.resolve_func_name(node.__class__.__name__)
    if func is None: # fail to find the function, use the generic function
      self.gen_generic(node)
    else: # found the function, call it
      func(node)
      # set selected style
      self.set_selected_style_speech_for_node(node)

    return

  def resolve_func_name(self, node_type: str):
    '''
    find the speech gen function given a tree node class name. For an ast.XXX
    class, its generation function name is "gen_ast_XXX"
    '''
    
    func_name = f"gen_ast_{node_type}"

    # check if function exist
    if hasattr(self, func_name) and callable(func := getattr(self, func_name)):
      # exist return the function
      return func
    else:
      # does not exist
      return None

  def set_speech_style(self, node_class, style:str):
    '''
    Set speech style for a type of AST node (i.e., ast node class)
    '''
    self.speech_styles[node_class] = style
    return

  def get_speech_style(self, node_class):
    '''
    Get the speech style for a type of class
    '''
    return self.speech_styles[node_class]

  def set_selected_style_speech_for_node(self, node):
    '''
    This function is called automatically after each gen_ast_XXX function
    to select the "selected_style" field of jvox_speech.
    If user does not set the speech style for a type of node, "default" is
    used.
    '''
    if node.__class__ in self.speech_styles:
      # user selects a style, use that style
      if self.speech_styles[node.__class__] in node.jvox_speech:
        node.jvox_speech["selected_style"] = (
          node.jvox_speech[self.speech_styles[node.__class__]])
      else:
        raise ValueError(f"Style \"{self.speech_styles[node.__class__]}\" has "
                         f"not been generated for node {node}")
    else:
      # user does not select a style, use "default"
      node.jvox_speech["selected_style"] = node.jvox_speech["default"]

  def gen_generic(self, node):
    '''
    Generic implementation for speech generation for a tree node. This generic
    function is used to handle the AST node types who's speech generation code
    has not been implemented yet.
    
    This implementation does not generate a new speech. Instead, it goes over
    the children of "node", and find the first the child with a speech stored in
    "speeches", and use this speech as the speech for "node"
    '''
    
    # default to no speech
    # self.speeches[node] = "error, no speech"
    node.jvox_speech = {"default":"error, no speech"}

    # visit all desendents, find which one has a speech, use that speech
    for field, value in ast.iter_fields(node):
      if isinstance(value, list):
        for item in value:
          if isinstance(item, ast.AST) and hasattr(item, "jvox_speech"):
            # has a speech, use it
            node.jvox_speech = item.jvox_speech
            break
      elif isinstance(value, ast.AST) and hasattr(value, "jvox_speech"):
        # has a speech, use it
        node.jvox_speech = value.jvox_speech
        break

    return

  def gen_ast_Load(self, node):
    '''
    Do nothing. Not a read-able class.
    '''
    node.jvox_speech={"default":""}
    return



