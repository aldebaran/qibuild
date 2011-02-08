#!/usr/bin/env python


## Copyright (C) 2011 Aldebaran Robotics


import sys

HEADER = """## Copyright (C) 2011 Aldebaran Robotics
"""

def fix_file(filename):
    start_header = -1
    end_header = -1
    was_in_header = False
    seen_header = False
    seen_shebang = False
    with open(filename, "r") as fp:
        lines = fp.readlines()

    for (i, line) in enumerate(lines):
        if line.startswith("#!"):
            seen_shebang = True
            continue
        if line.startswith("#"):
            if not seen_header:
                start_header = i
                was_in_header = True
                seen_header = True
                continue
        else:
            if was_in_header:
                end_header = i
                was_in_header = False
                continue

    header_lines = [l + "\n" for l in HEADER.splitlines()]
    if not seen_header:
        if seen_shebang:
            new_lines = [lines[0]] + header_lines + lines[1:]
        else:
            new_lines = header_lines + lines
    else:
        new_lines = lines[:start_header] +\
                    header_lines +\
                    lines[end_header:]

    with open(filename, "w") as fp:
        fp.writelines(new_lines)


if __name__ == "__main__":
    for file in sys.argv[1:]:
        print "fixing ", file
        fix_file(file)

