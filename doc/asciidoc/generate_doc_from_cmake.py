#!/usr/bin/env python
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##
import sys
import re
import os

funcregex = re.compile('\s*function\s*\((\S*?)[\s\)]+.*')
nameregex = re.compile('# \\\\(\S*?):(\S*?)\s+(.*)')

def addAsciiDocLine(line, doclines):
    if line.startswith("# ==== ") or line.startswith("# === ") or line.startswith("# == ") or line.startswith("# ."):
        doclines.append("")
        doclines.append(line[2:])
        return 1
    #indent asciidoc bis
    elif line.startswith("# WARNING:") or line.startswith("# NOTE:") or line.startswith("# IMPORTANT:") or line.startswith("# CAUTION:") or line.startswith("# TIP:"):
        doclines.append("")
        doclines.append(line[2:])
        return 1
    return None

class FunctionContext:
    """ store the documentation of a function """
    def __init__(self, exampledir):
        self.name     = None
        self.desc     = None
        self.args     = dict()
        self.argn     = None
        self.flags    = dict()
        self.params   = dict()
        self.groups   = dict()
        self.examples = dict()
        self.exampledir = exampledir

    def _extractName(self, dp):
        """ extract a command with it's name and a description
            # \cmd:name description
            #           extended description
        """
        match = nameregex.match(dp.preview_line())
        if match:
            dp.get_line()
            (name, value, desc) = match.groups(1)
            desc = [ desc.strip() ]
            desc.extend(self._extractBlock(dp))
            return (name, value, desc)
        return None
        pass

    def _extractBlock(self, dp):
        """ extract a block
            will stop if the next line is not a comment or is a command
        """
        doclines = list()
        line = dp.preview_line()
        while line.startswith("#") and not line.startswith("# \\"):
            if addAsciiDocLine(dp.preview_line(), doclines):
                dp.get_line()
                continue
            doclines.append(dp.get_line()[2:].strip())
            line = dp.preview_line()
        return doclines

    def extractCommand(self, dp):
        """ extract doxygen like command """
        ret = self._extractName(dp)
        if ret:
            #print "matched: %s - %s : %s" % (ret[0], ret[1], ret[2])
            (name, value, desc) = ret
            if name == "arg":
                self.args[value]   = (desc)
            elif name == "argn":
                self.argn          = (value, desc)
            elif name == "flag":
                self.flags[value]  = (desc)
            elif name == "param":
                self.params[value] = (desc)
            elif name == "group":
                self.groups[value] = (desc)
            elif name == "example":
                self.examples[value] = (desc)
            else:
                print "WARNING: unknown command:", dp.preview_line()
        else:
            print "WARNING: unknown command:", dp.preview_line()
            dp.get_line()

    def extractFunctionName(self, dp):
        line = dp.get_line()
        name = funcregex.match(line)
        if name:
            name = name.groups(1)[0]
            self.name = name

    def extractDescription(self, dp):
        """ extract description """
        docline = list()
        #print "extract desc"
        docline.append(dp.get_line()[3:].strip())
        docline.extend(self._extractBlock(dp))
        self.desc = docline
        print "description:", "\n".join(self.desc)
        print ""

    def getDoc(self, sample):
        """ get an example """
        p = os.path.join(self.exampledir, sample)
        if not os.path.exists(p):
            p += ".cmake"
        if os.path.exists(p):
            with open(p, "r") as f:
                lines = f.readlines()
            lines = [ x.strip() for x in lines ]
            return lines
        return list()

    def generate(self):
        #this is doc only, not a function...
        docline = list()
        if self.name is None:
            docline.extend(self.desc)
            docline.append("")
            return docline

        docline.append("=== Function %s ===" % (self.name))
        docline.append(".*Description*")
        docline.extend(self.desc)
        docline.append("")

        docline.append(".*Prototype*")
        docline.append("[source,cmake]")
        docline.append("----")
        arg = "  %s(" % self.name
        for k in self.args.keys():
            arg += "<%s> " % k.lower()
        if self.argn:
            arg += ".. "
        if arg[-1] == " ":
            arg = arg[:-1]
        docline.append(arg)

        indent = " " * len("  %s(" % self.name)
        for k in self.flags.keys():
            docline.append(indent + "%s" % k.upper())
        for k in self.params.keys():
            docline.append(indent + "%s <%s>" % (k.upper(), k.lower()))
        for k in self.groups.keys():
            docline.append(indent + "%s <%s> .." % (k.upper(), k.lower()))
        docline[-1] = docline[-1] + ")"
        docline.append("----")
        docline.append("")


        docline.append(".*Parameters*")
        for (k, v) in self.args.iteritems():
            docline.append(" * <%s>: %s" % (k.lower(), " ".join(v)))
        if self.argn:
            docline.append(" * ARGN(%s): %s" % (self.argn[0], self.argn[1]))
        for (k, v) in self.flags.iteritems():
            docline.append(" * %s: %s" % (k.upper(), " ".join(v)))
        for (k, v) in self.params.iteritems():
            docline.append(" * %s <%s>: %s" % (k.upper(), k.lower(),  " ".join(v)))
        for (k, v) in self.groups.iteritems():
            docline.append(" * %s <%s> .. : %s" % (k.upper(), k.lower(),  " ".join(v)))
        docline.append("")

        for (k, v) in self.examples.iteritems():
            docline.append(".*Example* %s" % k)
            docline.append("[source,cmake]")
            docline.append("----")
            docline.extend(self.getDoc(k))
            #TODO: source the sample
            docline.append("----")
            docline.append("")

        return docline

class CmakeDocParser:
    """ parse a cmake document containing doc """
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


def doc_process_command(dp, fc):
    doclines = []
    line = dp.preview_line()
    if line.startswith("#!"):
        fc.extractDescription(dp)
    #indent asciidoc
    #elif addAsciiDocLine(line, doclines):
    #    dp.get_line()
    #handle command
    elif line.startswith("# \\"):
        fc.extractCommand(dp)
    else:
        doclines.append(dp.get_line())
    return doclines

def doc_process(dp, exampledir):

    getdoc = 0
    doclines = list()
    fc = FunctionContext(exampledir)
    while dp.has_next():
        current_index = dp.index
        line = dp.preview_line()

        #this is a function
        if line.startswith("function") and getdoc:
            fc.extractFunctionName(dp)
            doclines.extend(fc.generate())
            fc = FunctionContext(exampledir)
            getdoc = 0
            #print "getdoc0:", line

        #this is not doc... pass
        if line.startswith("#!"):
            #print "getdoc1:", line
            getdoc = 1

        if not getdoc:
            dp.get_line()
            continue

        #this is not doc... pass
        if not line.startswith("#"):
            doclines.extend(fc.generate())
            getdoc = 0
            dp.get_line()
            continue


        #try to see if it's asciidoc related
        if getdoc:
            doclines.extend(doc_process_command(dp, fc))
        if dp.index == current_index:
            print "Parse error: line(%d): %s" % (current_index, dp.preview_line())
            exit(1)
    return doclines

def extract_doc_from_cmake(fname, exampledir):
    """
    return a list with line of doc
    """
    with open(fname, "r") as f:
        lines = f.readlines()
    dp = CmakeDocParser(lines)
    doclines = doc_process(dp, exampledir)
    #print doclines
    docs = "\n".join(doclines)
    return docs

def generate_doc(fname, exampledir, outdir):
    """ generate a .txt based on a cmake file if the doc is not empty """
    dest = os.path.join(outdir, os.path.basename(fname))
    dest = dest.replace(".cmake", ".txt")
    docs = extract_doc_from_cmake(fname, exampledir)

    if len(docs) > 0:
        print "Generated:", dest
        with open(dest, "w") as f:
            for l in docs:
                f.write(l)

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
    example = sys.argv[2]
    dest = sys.argv[3]
    try:
        os.makedirs(dest)
    except OSError:
        pass
    cmakefiles = ls(src, ".*\.cmake")
    for f in cmakefiles:
        if f.endswith("_test.cmake"):
            continue
        generate_doc(f, example, dest)
