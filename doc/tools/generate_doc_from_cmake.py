#!/usr/bin/env python
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

# This program parse cmake files and generate asciidoc.
#
# Doc block should be formated like that:
#
# a block:
# #!
# # ...
# #
# function(name)
#
# another block:
# #!
# # ...
# #
#


import sys
import re
import os

EXAMPLE_DIR=""

class DocBlock:
    """ simple doc block, representing an asciidoc block.
    """
    def __init__(self, content):
        self.content = LineHolder(content)
        self.result  = None
        self.apply_lite_formatter()
        #self.content = content

    def apply_lite_formatter(self):
        """ add space before title and NOTE/WARNING/... """
        doclines = list()
        prev = ""
        for line in self.content.lines:
            if line.startswith("# ==== ") or line.startswith("# === ") or line.startswith("# == ") or line.startswith("# ."):
                if prev != "":
                    doclines.append("")
            elif line.startswith("# WARNING:") or line.startswith("# NOTE:") or line.startswith("# IMPORTANT:") or line.startswith("# CAUTION:") or line.startswith("# TIP:"):
                if prev != "":
                    doclines.append("")
            prev = line
            doclines.append(line)
        self.content = LineHolder(doclines)

    def extract_block(self):
        """ extract a block of doc, everything till the next command """
        doclines = list()

        while self.content.has_next():
            line = self.content.preview_line()
            if line.startswith("\\"):
                break
            doclines.append(self.content.get_line())
        return doclines

    def extract_command_name(self):
        """ extract a command with it's name and a description
            # \cmd:name description
            #           extended description
        """
        commandregex = re.compile('\\\\(\S*?):(\S*)(.*)')
        match = commandregex.match(self.content.preview_line())
        if match:
            self.content.get_line()
            (command, value, desc) = match.groups(1)
            desc = [ desc.strip() ]
            desc.extend(self.extract_block())
            return (command, value, desc)
        return None

    def extract_command(self):
        """
        handle command
        """
        ln = self.content.preview_line()
        (command, value, desc) = self.extract_command_name()
        if command == "example":
            self.result.extend(self.generate_example(value, desc))
        else:
            print "WARNING unknow command:", command, value, desc

    def generate_example(self, value, desc):
        """ get an example """
        docline = list()
        p = os.path.join(EXAMPLE_DIR, value)
        if not os.path.exists(p):
            p += ".cmake"
        if not os.path.isfile(p):
            p = os.path.join(EXAMPLE_DIR, value, "CMakeLists.txt")
        if os.path.exists(p):
            lines = list()
            try:
                with open(p, "r") as f:
                    lines = f.readlines()
            except IOError:
                print "Error: example not found: ", p
                pass
            lines = [ x.rstrip() for x in lines ]
            docline.append("")
            docline.append("=== Example: %s ===" % value)
            docline.append("[source,cmake,numbered]")
            docline.append("----")
            docline.extend(lines)
            docline.append("----")
            docline.append("")
        else:
            print "sample not found:", p
        return docline

    def generate(self):
        """ generate the asciidoc output for this block
        """
        self.result = list()
        while self.content.has_next():
            line = self.content.preview_line()
            if line.startswith("\\"):
                self.extract_command()
                continue
            self.result.append(self.content.get_line())

    def __str__(self):
        if not self.result:
            self.generate()
        return "\n".join(self.result)



class FunctionBlock(DocBlock):
    """ handle a function doc block """
    def __init__(self, function_name, content):
        DocBlock.__init__(self, content)
        self.commands = dict()
        self.valid_commands = ('arg', 'argn', 'flag', 'param', 'group', 'example')
        for k in self.valid_commands:
            self.commands[k] = dict()
        self.name = self.extract_function_name(function_name)
        self.extract_commands()

    def extract_commands(self):
        """ extract command and store them to self.commands
            the remanaining self.content.lines is "command free"
        """
        doclines = list()
        prev = ""
        while self.content.has_next():
            line = self.content.preview_line()
            if line.startswith("\\"):
                self.extract_command()
            else:
                self.content.get_line()
                doclines.append(line)
        self.content = LineHolder(doclines)

    def extract_function_name(self, function_name):
        """ extract a function name """
        funcregex = re.compile('\s*function\s*\((\S*?)[\s\)]+.*')
        name = funcregex.match(function_name)
        if name:
            name = name.groups(1)[0]
            return name
        return None

    def extract_command(self):
        """ extract a command """
        (command, value, desc) = self.extract_command_name()
        if not self.commands.get(command):
            self.commands[command] = dict()
        self.commands[command][value] = desc

        if command not in self.valid_commands:
            print "WARNING: unknown command:", command, value, desc


    def generate(self):
        """ generate the asciidoc for this block """
        self.result = list()
        self.result.extend(self.generate_function())
        for k,v in self.commands['example'].iteritems():
            print "example:", k
            self.result.extend(self.generate_example(k, v))
        return self.result

    def generate_function(self):
        """ generate documentation for a function
        """
        docline = list()
        docline.append("")
        docline.append("== %s ==" % (self.name))
        docline.append("=== Description ===")
        docline.extend(self.content.lines)
        docline.append("")

        docline.append("=== Prototype ===")
        docline.append("[format=\"csv\",cols=\"4\",align=\"left\"]")
        docline.append("[frame=\"none\",grid=\"none\",options=\"autowidth\"]")
        docline.append("|======")
        #docline.append("[source,cmake]")
        #docline.append("----")
        arg = "+*[red]#%s#*(+," % self.name
        for k in self.commands['arg'].keys():
            arg += "+_<%s>_+ " % k.lower()
        if self.commands.get('argn'):
            arg += "+_.._+ "
        if arg[-1] == " ":
            arg = arg[:-1]
        arg += ",,"
        docline.append(arg)

        for k in self.commands['flag'].keys():
            docline.append(",+*%s*+,," % k.upper())
        for k in self.commands['param'].keys():
            docline.append(",+*%s*+, +_<%s>_+," % (k.upper(), k.lower()))
        for k in self.commands['group'].keys():
            docline.append(",+*%s*+, +_<%s> .._+," % (k.upper(), k.lower()))
        docline[-1] = docline[-1] + "+)+"
        docline.append("|======")
        docline.append("")

        docline.append("=== Parameters ===")
        for (k, v) in self.commands['arg'].iteritems():
            docline.append(" * _<%s>_: %s" % (k.lower(), " ".join(v)))
        if self.commands.get('argn'):
            docline.append(" * _<remaining args>_ .. : %s" % " ".join(self.commands['argn'].values()[0]))
        for (k, v) in self.commands['flag'].iteritems():
            docline.append(" * *%s*: %s" % (k.upper(), " ".join(v)))
        for (k, v) in self.commands['param'].iteritems():
            docline.append(" * *%s* _<%s>_: %s" % (k.upper(), k.lower(),  " ".join(v)))
        for (k, v) in self.commands['group'].iteritems():
            docline.append(" * *%s* _<%s>_ .. : %s" % (k.upper(), k.lower(),  " ".join(v)))
        docline.append("")
        return docline



class LineHolder:
    """ simple class to store and fetch lines
    """
    def __init__(self, lines):
        self.lines = lines
        self.index = 0

    def preview_line(self):
        return self.lines[self.index]
        pass

    def get_line(self):
        line = self.lines[self.index]
        self.index += 1
        return line

    def has_next(self):
        return self.index < len(self.lines)


class CMakeDocParser:
    """ Extract doc from a cmake like file
        This class strip # and #! from lines
    """

    def __init__(self, lines):
        self.dp = LineHolder(lines)
        self.blocks = list()
        self.current_block = list()

    def cleanup_line(self, line):
        """ remove comment from a line """
        if line.startswith("#!") or line.startswith("# "):
            return line[2:].strip()
        elif line.startswith("#"):
            return line[1:].strip()
        return line.strip()

    def eat_shit(self):
        """ eat line that are not part of the doc """
        while self.dp.has_next():
            line = self.dp.preview_line()
            stripped = line.strip()
            if stripped.startswith("#!"):
                break
            self.dp.get_line()

    def eat_block(self):
        """ extract a block
            will stop if the next line is not a comment or not a function declaration
        """
        doclines = list()

        while self.dp.has_next():

            line = self.dp.preview_line()
            stripped = line.strip()

            if stripped.startswith("#"):
                doclines.append(self.cleanup_line(line))
                self.dp.get_line()
            elif stripped.startswith("function"):
                self.dp.get_line()
                self.blocks.append(FunctionBlock(self.cleanup_line(line), doclines))
                break
            else:
                self.blocks.append(DocBlock(doclines))
                break

    def parse_block(self):
        """ parse all block
        this will populate self.block with DocBlock and FunctionBlock
        """
        while self.dp.has_next():
            current_index = self.dp.index
            self.eat_shit()
            self.eat_block()
            if current_index == self.dp.index:
                print "parse internal error (because I love this error message)"
                return


def extract_doc_from_cmake(fname):
    """
    return a list with line of doc
    """
    with open(fname, "r") as f:
        lines = f.readlines()

    dp = CMakeDocParser(lines)
    dp.parse_block()

    docs = list()
    for b in dp.blocks:
        docs.append(str(b))
        #     print ""
        #     print "================================================"
        #     print "================================================"
        #     print b
    return docs

def generate_doc(fname, outdir):
    """ generate a .txt based on a cmake file if the doc is not empty """
    dest = os.path.join(outdir, os.path.basename(fname))
    dest = dest.replace(".cmake", ".txt")
    docs = extract_doc_from_cmake(fname)

    if len(docs) > 0:
        print "Generated:", dest
        with open(dest, "w") as f:
            for l in docs:
                f.write(l + '\n')

def ls(directory, pattern):
    """ return file list that match pattern """
    filesanddir = os.listdir(directory)
    ret = list()
    for r in filesanddir:
        p = os.path.join(directory, r)
        if os.path.isfile(p) and re.match(pattern, p):
            ret.append(p)
    return ret

def usage():
    print "usage:"
    print "generate_doc_from_cmake source_dir example_dir dest_dir"
    exit(2)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage()
    src = sys.argv[1]
    EXAMPLE_DIR = sys.argv[2]
    dest = sys.argv[3]
    try:
        os.makedirs(dest)
    except OSError:
        pass
    cmakefiles = ls(src, ".*\.cmake")
    for f in cmakefiles:
        if f.endswith("_test.cmake"):
            continue
        generate_doc(f, dest)
