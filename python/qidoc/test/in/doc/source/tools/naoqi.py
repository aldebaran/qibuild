"""
Sphinx domain for documenting NAOqi-specific concepts such as events, memory
keys and modules.


This domain heavily borrows from the C one.

Oddities:

- variables (memory keys and event data) types link back to the corresponding
  cpp type.

Limitations:

- event signature parsing is rudimentary. It should be enough though.

- permalink to events are similar to the C ones: no support for overload.

"""

__author__ = (u"Sebastien BARTHELEMY <sbarthelemy@aldebaran-robotics.com>")
__copyright__ = u"Copyright (C) 2011 Aldebaran Robotics"

import re
import string
import sphinx
from docutils import nodes
from sphinx import addnodes
from sphinx.util.docfields import DocFieldTransformer
from sphinx.locale import l_, _
from sphinx.domains import ObjType, Index
from sphinx.util.docfields import TypedField
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

# REs for signatures
memkey_sig_re = re.compile(
    r'''^([a-zA-Z0-9_:]*)\s+   # type
         (\w*)\s*$             # name
         ''', re.VERBOSE)
event_sig_re = re.compile(
    r'''^([a-zA-Z0-9_:]+)  \s* # name
        (?: \((.*)\) )?$       # optionally arguments
        ''', re.VERBOSE)
wsplit_re = re.compile(r'([^a-zA-Z0-9_:]+)')
stopwords = set(('const', 'void', 'FILE', 'struct'))

def _parse_type(node, argtype):
    # add cross-ref nodes for all words
    for part in filter(None, wsplit_re.split(argtype)):
        tnode = nodes.Text(part, part)
        if part[0] in string.ascii_letters+'_'+':' and \
               part not in stopwords:
            pnode = sphinx.addnodes.pending_xref(
                '', refdomain='cpp', reftype='type', reftarget=part,
                modname=None, classname=None)
            pnode += tnode
            node += pnode
        else:
            node += tnode

class NaoQiObject(sphinx.directives.ObjectDescription):

    def add_target_and_index(self, name, sig, signode):
        signode['ids'].append(name)
        self.state.document.note_explicit_target(signode)
        inv = self.env.domaindata['naoqi'][self.objtype]
        if name in inv:
            msg = 'duplicate NAOqi {0} description of {1}, other instance ' \
                  'in {2}'.format(self.objtype, name,
                                  self.env.doc2path(inv[name]))
            self.env.warn(self.env.docname, msg, self.lineno)
        inv[name] = self.env.docname
        indextext = u"{0} ({1})".format(name, self.objtype_pretty)
        self.indexnode['entries'].append(('single', indextext, name, name))

class NaoQiMemKey(NaoQiObject):

    objtype_pretty = u"ALMemory key"

    def handle_signature(self, sig, signode):
        """
        Transform a memory key signature into RST nodes.
        Returns the name of the event
        """
        m = memkey_sig_re.match(sig)
        if m is None:
            raise ValueError
        type, name = m.groups()
        signode += addnodes.desc_type('', '')
        _parse_type(signode[-1], type)
        #_parse_type(signode, type)
        signode += nodes.Text(" ")
        signode += sphinx.addnodes.desc_name(name, name)
        return name

class NaoQiEvent(NaoQiObject):

    objtype_pretty = u"NAOqi event"

    doc_field_types = [
            TypedField('parameter', label=l_('Parameters'),
                       names=('param', 'parameter', 'arg', 'argument'),
                       typerolename='type', typenames=('type',)),
            ]

    def handle_signature(self, sig, signode):
        """
        Transform an event signature into RST nodes.
        Returns the name of the event
        """
        m = event_sig_re.match(sig)
        if m is None:
           # todo: add warning
            raise ValueError
        (name, arglist) = m.groups()
        line0 = nodes.line('', u"Event: ")
        line0 += sphinx.addnodes.desc_name(name, '"' + name + '"')
        if arglist is None:
            return name
        signode += line0
        signode += nodes.Text(u'callback')
        paramlist = addnodes.desc_parameterlist()
        arglist = arglist.replace('`', '').replace('\\ ', '') # remove markup
        args = arglist.split(',')
        args.insert(0, u'std::string eventName')
        args.append(u'std::string subscriberIdentifier')
        for arg in args:
            arg = arg.strip()
            if not arg:
                continue
            param = addnodes.desc_parameter('', '', noemph=True)
            try:
                argtype, argname = arg.rsplit(' ', 1)
            except ValueError:
                # no argument name given, only the type
                argtype = arg
                _parse_type(param, argtype)
            else:
                _parse_type(param, argtype)
                param += nodes.emphasis(argname, ' '+argname)
            paramlist += param
        signode += paramlist
        return name

    def run(self):
        """
        Main directive entry function, called by docutils upon encountering the
        directive.

        This directive is meant to be quite easily subclassable, so it delegates
        to several additional methods.  What it does:

        * find out if called as a domain-specific directive, set self.domain
        * create a `desc` node to fit all description inside
        * parse standard options, currently `noindex`
        * create an index node if needed as self.indexnode
        * parse all given signatures (as returned by self.get_signatures())
          using self.handle_signature(), which should either return a name
          or raise ValueError
        * add index entries using self.add_target_and_index()
        * parse the content and handle doc fields in it

        This method was copied and adapted from
        sphinx.directive.ObjectDescription.run() (in Sphinx 1.1)

        """
        if ':' in self.name:
            self.domain, self.objtype = self.name.split(':', 1)
        else:
            self.domain, self.objtype = '', self.name
        self.env = self.state.document.settings.env
        self.indexnode = addnodes.index(entries=[])

        node = addnodes.desc()
        node.document = self.state.document
        node['domain'] = self.domain
        # 'desctype' is a backwards compatible attribute
        node['objtype'] = node['desctype'] = self.objtype
        node['noindex'] = noindex = ('noindex' in self.options)

        self.names = []
        signatures = self.get_signatures()
        name = None
        for i, sig in enumerate(signatures):
            # add a signature node for each signature in the current unit
            # and add a reference target for it
            signode = addnodes.desc_signature(sig, '')
            signode['first'] = False
            node.append(signode)
            try:
                # name can also be a tuple, e.g. (classname, objname);
                # this is strictly domain-specific (i.e. no assumptions may
                # be made in this base class)
                name = self.handle_signature(sig, signode)
            except ValueError:
                # signature parsing failed
                signode.clear()
                signode += addnodes.desc_name(sig, sig)
                continue  # we don't want an index entry here
            if not noindex and name is not None and name not in self.names:
                # only add target and index entry if this is the first
                # description of the object with this name in this desc block
                self.names.append(name)
                self.add_target_and_index(name, sig, signode)

        contentnode = addnodes.desc_content()
        node.append(contentnode)
        if self.names:
            # needed for association of version{added,changed} directives
            self.env.temp_data['object'] = self.names[0]
        self.before_content()
        self.state.nested_parse(self.content, self.content_offset, contentnode)
        for child in contentnode:
            if isinstance(child, nodes.field_list):
                child.insert(0, nodes.field('',
                    nodes.field_name('', u'param std::string eventName'),
                    nodes.field_body('', nodes.paragraph('', u'"{0}"'.format(name)))))
                child.append(nodes.field('',
                    nodes.field_name('', u'param std::string subscriberIdentifier'),
                    nodes.field_body('', nodes.paragraph('', u''))))

        DocFieldTransformer(self).transform_all(contentnode)
        self.env.temp_data['object'] = None
        self.after_content()
        return [self.indexnode, node]

class NAOqiIndex(Index):
    """
    Index subclass to provide the Python module index.
    """

    def generate(self, docnames=None):
        # entries = content.setdefault("l", [])
        # entries.append(["LogManager", 1, '', '', '', '', ''])
        # entries.append(["LogManager.logError", 2, 'logmanager', 'logWarning', '', '', ''])
        # entries.append(["LogManager.logWarning", 2, 'logmanager', 'logError', '', '', ''])

        content = {}

        for ev, modname in sorted(self.domain.data[self._data].iteritems()):
            entries = content.setdefault(ev[0].lower(), [])
            entries.append([ev, 2, modname, ev, '', '', ''])

        # sort by first letter
        result   = sorted(content.iteritems())
        collapse = False

        return result, collapse

class NAOqiEventIndex(NAOqiIndex):
    name = 'eventindex'
    localname = l_('NAOqi Event Index')
    shortname = l_('events')
    _data = 'event'

class NAOqiMemoryIndex(NAOqiIndex):
    name = 'memoryindex'
    localname = l_('NAOqi Memory Key Index')
    shortname = l_('memorykeys')
    _data = 'memkey'

class NaoQiDomain(sphinx.domains.Domain):
    name = 'naoqi'
    label = 'NAOqi'

    object_types = {
            'event': ObjType(l_('event'), 'event'),
            'memkey': ObjType(l_('memory key'), 'memkey'),
    }
    directives = {
            'event': NaoQiEvent,
            'memkey': NaoQiMemKey,
    }
    roles = {
            'event': XRefRole(fix_parens=True),
            'memkey': XRefRole(),
    }
    initial_data = {
            'event': {}, # fullname -> docname
            'memkey': {}, # fullname -> docname
    }
    indices = [
        NAOqiEventIndex,
        NAOqiMemoryIndex,
    ]

    def clear_doc(self, docname):
        for objtype in (u'event', u'memkey'):
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
    app.add_domain(NaoQiDomain)
