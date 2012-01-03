## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""
Sphinx domain for documenting CMake functions


"""
import docutils


import sphinx
from sphinx import addnodes
from sphinx.locale import l_
from sphinx.domains import ObjType
from sphinx.util.docfields import TypedField, Field

class CMakeFunction(sphinx.directives.ObjectDescription):
    doc_field_types = [
        TypedField('arg', label=l_('Arguments'),
                   names=['arg']),
    ]
    def handle_signature(self, sig, signode):
        """
        Transform a CMake function signature
        into RST nodes
        """
        nb_param = len(sig.split(" "))
        code = sig.replace("] ", "]\n    ")
        if nb_param > 1:
            code = code.replace(")", "\n)")
        literal = docutils.nodes.literal_block(code, code)
        literal['language'] = 'cmake'
        signode += literal

class CMakeDomain(sphinx.domains.Domain):
    name = 'cmake'
    label = 'CMake'

    object_types = {
            'function': ObjType(l_('functions'), 'functions'),
    }
    directives = {
            'function': CMakeFunction,
    }



def setup(app):
    app.add_domain(CMakeDomain)
