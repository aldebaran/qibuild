##
## Copyright Aldebaran Robotics 2011
##

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
    return "\n".join([indent + x for x in txt.splitlines()])


def clean_indent(txt):
    """ Useful because parameters descriptions
    are not always properly indented at the end of
    parsing

    """
    return "\n".join([x.strip() for x in txt.splitlines()])


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


def gen_params_rst(params):
    """ Generate rst doc from a parameter

    """
    if not params:
        return ""

    res = """**Parameters**

"""

    for param in params:
        (type_, name, doc) = param

        res += """*{name}*

{doc}

""".format(name=name, doc=indent(doc, 1))

    return res


def gen_usage_rst(fun_name, params):
    """ Generate rst doc for usage of a function

    """
    usage = ""
    for (type, name, doc_) in params:
        if type == "arg":
            usage += name
        elif type == "flag":
            usage += "[%s]" % name
        elif type == "param":
            usage += "%s <%s>" % (name, name.lower())
        elif type == "group":
            usage += "%s <%s> ..." % (name, name.lower())
        elif type == "argn":
            usage += "[<%s> ...]" % (name)
        elif type == "example":
            # \example is handled by gen_example_rst
            pass

        else:
            print "unknown type: ", type
        usage += "\n"
    if len(params) > 1:
        usage = indent(usage, 2)
        usage = "%s(\n%s\n)" % (fun_name, usage)
    else:
        usage = usage[:-1] # remove usless \n
        usage = "%s(%s)" % (fun_name, usage)

    res = """

.. code-block:: cmake

{usage}
""".format(usage=indent(usage, 1))

    return res


def gen_example_rst(example):
    r"""

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
    Should be at the top of the file, from then
    first '#!' to the next title block

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
    params_rst = gen_params_rst(params)

    usage = gen_usage_rst(name, params)
    example_rst = gen_example_rst(example)


# We generate an index AND a ref, because
# writing a CMake domain is a little hard
# and prbably overkill
    res = """.. index::
  single: {name}

.. _{name}:

{name}
{h2}
{usage}
{desc}
{params}
{example}

""".format(name=name,
           h2="-"*len(name),
           desc=desc,
           usage=usage,
           params=params_rst,
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
    if len(sys.argv) != 2:
        print "Usage: gen_cmake_doc /path/to/qibuild"
        sys.exit(1)
    qibuild_dir = sys.argv[1]
    qibuild_dir = os.path.abspath(qibuild_dir)
    this_file = __file__
    this_dir = os.path.dirname(this_file)
    cmake_api = os.path.join(this_dir, "../cmake/api")
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
