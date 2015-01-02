## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""
Sphinx domain for documenting CMake functions


"""
import docutils


import sphinx
from sphinx.roles import XRefRole
from sphinx import addnodes
from sphinx.locale import l_
from sphinx.domains import ObjType, Index
from sphinx.util.docfields import TypedField, Field
from sphinx.util.nodes import make_refnode

class CMakeFunctionIndex(Index):
    name = 'functions-index'
    localname = l_('CMake functions Index')
    shortname = l_('cmake functions')
    _data = 'function'

    def generate(self, docnames=None):
        content = {}
        for ev, modname in sorted(self.domain.data[self._data].iteritems()):
            entries = content.setdefault(ev[0].lower(), [])
            entries.append([ev, 2, modname, ev, '', '', ''])
        # sort by first letter
        result   = sorted(content.iteritems())
        collapse = False
        return result, collapse


class CMakeFunction(sphinx.directives.ObjectDescription):
    objtype_pretty = u"CMake function"
    doc_field_types = [
        TypedField('arg', label=l_('Arguments'),
                   names=['arg']),
    ]
    def add_target_and_index(self, name, sig, signode):
        signode['ids'].append(name)
        self.state.document.note_explicit_target(signode)
        inv = self.env.domaindata['cmake'][self.objtype]
        if name in inv:
            msg = 'duplicate CMake {0} description of {1}, other instance ' \
                  'in {2}'.format(self.objtype, name,
                                  self.env.doc2path(inv[name]))
            self.env.warn(self.env.docname, msg, self.lineno)
        inv[name] = self.env.docname
        indextext = u"{0} ({1})".format(name, self.objtype_pretty)
        self.indexnode['entries'].append(('single', indextext, name, name))

    def handle_signature(self, sig, signode):
        """
        Transform a CMake function signature
        into RST nodes.

        Return a name to add to the index
        """
        nb_param = len(sig.split(" "))
        code = sig.replace("] ", "]\n    ")
        if nb_param > 1:
            code = code.replace(")", "\n)")
        literal = docutils.nodes.literal_block(code, code)
        literal['language'] = 'cmake'
        signode += literal
        name = sig.split("(")[0]
        return name

class CMakeDomain(sphinx.domains.Domain):
    name = 'cmake'
    label = 'CMake'

    object_types = {
            'function': ObjType(l_('functions'), 'functions'),
    }
    directives = {
            'function': CMakeFunction,
    }
    initial_data = {
        'function': {}
    }
    roles = {
        'function' : XRefRole()
    }
    indices = [
        CMakeFunctionIndex,
    ]

    def clear_doc(self, docname):
        for objtype in (u'function',):
            for (objname, objdocname) in self.data[objtype].items():
                if objdocname == docname:
                    del self.data[objtype][objname]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        try:
            todocname = self.data[typ][target]
        except KeyError:
            return None
        return make_refnode(builder, fromdocname, todocname, target,
	        contnode, target)


def setup(app):
    app.add_domain(CMakeDomain)
