#!/usr/bin/env python


## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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

