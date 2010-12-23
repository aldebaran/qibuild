#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

CURDIR=$(dirname "$(readlink -f $0 2>/dev/null)")/

cd ${CURDIR}

python doc/tools/generate_doc_from_cmake.py \
  "cmake/qibuild" \
  "cmake/samples" \
  "build-doc"

PYTHONPATH=. python qibuild/tools/generate_asciidoc.py > "build-doc/qibuild-manpage.txt"

cp "/etc/asciidoc/javascripts/asciidoc-xhtml11.js" "build-doc"
cp "doc/asciidoc/pygments.css"                     "build-doc"
cp "doc/asciidoc/bare.css"                         "build-doc"
cp "cmake/qibuild/index.txt"                       "build-doc"

find ${CURDIR}/build-doc/ -type f -name '*.txt' | while read f ; do
  #asciidoc is stupid about css...
  #we desactivated default theme, set the stylesheet to bare.css, and disable embedded css
  asciidoc -a toc -a toclevels=1  -a linkcss -a 'theme=' -a stylesheet="bare.css" -a pygments "$f"
done

