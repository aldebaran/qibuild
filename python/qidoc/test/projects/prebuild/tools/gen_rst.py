## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
" Generate source/generated.rst "

def main():
    with open("source/generated.rst", "w") as fp:
        fp.write("""\
Generated section
=================

""")

if __name__ == "__main__":
    main()
