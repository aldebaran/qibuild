#!/usr/bin/env python
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##
import sys

def extract_doc_from_cmake(fname):
    with open(fname, "r") as f:
        lines = f.readlines()

    doclines = list()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue

        line = line[2:]
        if line.startswith("."):
            doclines.append("\n")
        if line.startswith("== "):
            doclines.append("\n")
        if line.startswith("=== "):
            doclines.append("\n")
        if line.startswith("==== "):
            doclines.append("\n")
        doclines.append(line)

    print "".join(doclines)
    with open(fname + ".txt", "w") as f:
        for l in doclines:
            f.write(l)

if __name__ == "__main__":
    extract_doc_from_cmake(sys.argv[1])
