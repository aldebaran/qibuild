## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate Sphinks documentation from a CMake source files.

"""

DOCUMENTED_FILES=[
    "log",
    "target",
    "stage",
    "install",
    "tests",
    "submodule",
    "option",
    "codegen",
    "python",
    "find",
    "flags",
    "gettext",
    "git",
    "swig/python",
    "swig/java",
    "subdirectory",
]

import re
import os
import sys

def clean_comment(line):
    r""" Clean up a comment, removing
    # , #! and starting space, and adding
    missing \n if necessary

    >>> clean_comment("#")
    '\n'
    >>> clean_comment("# This is ...")
    'This is ...\n'
    >>> clean_comment("#! This is ...")
    'This is ...\n'
    """
    if line.startswith("#!"):
        line = line[2:]
    else:
        line = line[1:]
    if line.startswith(" "):
        line = line[1:]
    if not line.endswith('\n'):
        line += '\n'
    return line


def indent(txt, indent_level):
    """ Indent a piece of text

    >>> indent('foo', 2)
    '    foo'
    """
    indent = "  " * indent_level
    return "\n".join(indent + x for x in txt.splitlines())


def clean_indent(txt):
    """ Useful because parameters descriptions
    are not always properly indented at the end of
    parsing

    """
    return "\n".join(x.strip() for x in txt.splitlines())


def parse_fun_block(txt):
    r""" Return a tuple of two elements:
    (fun_desc, params, example)
    where:
        * fun_desc is the general desription of the function
        * params is a list of tuples: (type, name, doc)
        * example is list of examples

    """
    desc = ""
    param_txt = ""
    in_desc = True
    for line in txt.splitlines():
        if line.startswith("\\"):
            in_desc = False
            param_txt += line + "\n"
        else:
            if in_desc:
                desc += line + "\n"
            else:
                param_txt += line + "\n"

    params = parse_params(param_txt)
    example = parse_example(txt)
    return (desc, params, example)



def parse_params(txt):
    """Parse a set of parameters doc

    Returns a list of tuples : (type, name, doc)

    """
    res =  list()
    # First, slipt with stuff looking like \TYPE:
    splitted = re.split(r'\s*\\(\w+)\s*:', txt)
    # We now have a list looking like:
    # ['', 'flag', '....', 'param', '...']
    i = 1
    while i < len(splitted) - 1:
        type = splitted[i]
        rest = splitted[i+1]
        if type == "argn":
            name = "remaining args"
            desc = rest
        else:
            # first word is the name, the rest is the description:
            match = re.match(r'\s*(\w+)\s*(.*)', rest, re.DOTALL)
            if not match:
                print "warning, failed to parse parameters"
                print "near", rest
                break
            (name, desc)= match.groups()
        desc = clean_indent(desc)
        res.append((type, name, desc))
        i += 2

    return res


def parse_example(txt):
    """ Parse a block of text linked to a function,
    looking for an example.

    Return None if not example was found
    """
    res = re.findall(r'\\example\s*:\s*(\w+)', txt, re.DOTALL)
    if not res:
        return
    if len(res) > 1:
        print "warning: only zero or one examples authorized for each function"
    return res[0]

def decorate(name, type):
    """ Decorate a parameter
    >>> decorate("foo", "arg")
    'foo'
    >>> decorate("foo", "flag")
    '[FOO]'
    >>> decorate("foo", "param")
    '[FOO foo]'
    >>> decorate("foo", "group")
    '[FOO <foo> ...]'
    >>> decorate("foo", "argn")
    None
    """
    if type == "arg":
        return name
    elif type == "flag":
        return "[%s]" % name
    elif type == "param":
        return "[%s <%s>]" % (name, name.lower())
    elif type == "group":
        return "[%s <%s> ...]" % (name, name.lower())
    elif type == "argn":
        return "[<%s> ...]" % (name)
    elif type == "example":
        # \example is handled by gen_example_rst
        return None
    return None


def gen_rst_directive(fun_name, params):
    """ Generate rst directive for a cmake function

    """
    res = ".. cmake:function:: %s" % fun_name
    res += "("
    sig_params = [decorate(name, type) for(type, name, doc) in params]
    sig_params = [x for x in sig_params if x is not None]
    sig_params = " ".join(sig_params)
    res += sig_params
    res += ")"
    res += "\n"
    res += "\n"
    for param in params:
        (type, name, doc) = param
        if type == "example":
            # \example is handled by gen_example_rst
            continue
        doc = doc.replace("\n", " ")
        to_add = ":arg %s: %s" % (name, doc)
        res += indent(to_add, 2)
        res += "\n"

    return res


def gen_example_rst(example):
    r""" Process the \example flag
    from cmake doc

    """
    if not example:
        return ""

    res =  """**Example**

.. literalinclude:: /samples/{example}/CMakeLists.txt
   :language: cmake

"""
    return res.format(example=example)

def get_title_block(txt):
    """ Get the general doc of the cmake code.
    Should be at the top of the file, from the
    first '#!' to the next text block

    """
    res = ""
    in_title = False
    for line in txt.splitlines():
        if line.startswith("#!"):
            in_title = True
            res += clean_comment(line)
            continue
        if in_title:
            if line.startswith("#"):
                res += clean_comment(line)
            else:
                break

    return res

def get_fun_name(line):
    """ Get function name from a line

    >>> get_fun_name('function(foo)')
    'foo'
    >>> get_fun_name('function(foo BAR BAZ)')
    'foo'
    >>> get_fun_name('function(foo')
    'foo'
    >>> get_fun_name('set(')
    """
    match = re.match(r'function\s*\((\w+)', line)
    if not match:
        return
    return match.groups()[0]

def get_fun_blocks(txt):
    """ Get all the blocks associated to a function,
    from '#!' to a line starting with function()

    Returns a list (function, txt)

    """
    res = list()
    cur_block = ""
    in_block = False
    for line in txt.splitlines():
        if line.startswith("#!"):
            in_block = True
            cur_block += clean_comment(line)
            continue
        if in_block:
            if line.startswith("#"):
                cur_block += clean_comment(line)
            else:
                if line.startswith('function'):
                    name = get_fun_name(line)
                    if name:
                        res.append((name, cur_block))
                    else:
                        print 'Warning: could not guess function name'
                        print 'near', line
                    cur_block = ""
                    in_block = False
                else:
                    cur_block = ""
                    in_block = False

    return res

def gen_title_rst(txt):
    """Generate rst title from a cmake comment

    """
    # Just add a few useful directives
    txt = ".. highlight:: cmake\n\n" + txt
    return txt

def gen_fun_rst(name, txt):
    """Generate rst documentation for a documentation from
    a name an a text

    """
    (desc, params, example) = parse_fun_block(txt)
    directive = gen_rst_directive(name, params)
    example_rst = gen_example_rst(example)


    res = """
{directive}
{desc}
{example}

""".format(name=name,
           directive=directive,
           desc=indent(desc, 2),
           example=example_rst)
    return res


def gen_rst(txt):
    """ Given a the contents of a cmake file
    with doxgen like comment, generate a RST
    formatted string.

    """
    res = ""

    title_block = get_title_block(txt)
    title_rst = gen_title_rst(title_block)
    res += title_rst
    # add a blank line just to be sure
    res += "\n"

    fun_blocks = get_fun_blocks(txt)
    for (name, fun_block) in fun_blocks:
        fun_rst = gen_fun_rst(name, fun_block)
        res += fun_rst

    return res


def gen_cmake_doc(cmake_file, rst_file):
    """ Creating the rst file matching a cmake
    file

    """
    should_skip = False
    basedir = os.path.dirname(rst_file)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    if not os.path.exists(rst_file):
        should_skip = False
    else:
        dest_mtime = os.stat(rst_file).st_mtime
        src_mtime  = os.stat(cmake_file).st_mtime
        if src_mtime < dest_mtime:
            should_skip = True
    if should_skip:
        return
    print "Generating", rst_file
    with open(cmake_file, "r") as fp:
        txt = fp.read()
    rst = gen_rst(txt)
    with open(rst_file, "w") as fp:
        fp.write(".. Generated by %s\n.. DO NOT EDIT\n\n" % sys.argv[0])
        fp.write(rst)

def main():
    """ Parses command line arguments

    """
    # We know that qidoc build will set the correct cwd
    qibuild_dir = ".."
    qibuild_dir = os.path.abspath(qibuild_dir)
    this_file = __file__
    this_dir = os.path.dirname(this_file)
    cmake_api = os.path.join(this_dir, "../source/advanced/cmake/api")
    cmake_api = os.path.abspath(cmake_api)
    if not os.path.exists(cmake_api):
        os.makedirs(cmake_api)
    qibuild_cmake = os.path.join(qibuild_dir, "cmake", "qibuild")

    for filename in DOCUMENTED_FILES:
        cmake_file = os.path.join(qibuild_cmake, filename + ".cmake")
        rst_file   = os.path.join(cmake_api    , filename + ".rst")
        gen_cmake_doc(cmake_file, rst_file)


if __name__ == "__main__":
    main()
