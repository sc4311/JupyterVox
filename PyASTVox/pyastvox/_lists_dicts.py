'''
This file defines additional member functions for the Class astparser, These
functions parse the Python lists and dictionaries.
'''

import ast

from speech import Speech

class lists_dicts_mixin:

  # generate speech for list
  def emit_List(self, node, level):
        speech = Speech()
        items = []

        # parse each item
        for i in range(len(node.elts)):
            speech = self.emit(node.elts[i])
            items.append(speech.text)
        
        speech.text = "list with items of " + ", ".join(items)

        return speech
