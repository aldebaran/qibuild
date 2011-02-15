#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

set -e

CURDIR=$(dirname "$(readlink -f $0 2>/dev/null)")/

cd ${CURDIR}/..

mkdir -p build-doc/images
python doc/tools/generate_doc_from_cmake.py \
  "cmake/qibuild" \
  "cmake/samples" \
  "build-doc"

if [ -f /etc/asciidoc/javascripts/asciidoc-xhtml11.js ] ; then
  cp "/etc/asciidoc/javascripts/asciidoc-xhtml11.js" "build-doc"
fi
cp "doc/asciidoc/pygments.css"                     "build-doc"
cp "doc/asciidoc/bare.css"                         "build-doc"

cp doc/*.txt                                        build-doc
cp -R doc/images/*                                  build-doc/images/

PYTHONPATH=python python doc/tools/generate_manpage_from_qibuild.py doc/qibuild-manpage.txt     build-doc/qibuild-manpage.txt     "qibuild.actions"
PYTHONPATH=python python doc/tools/generate_manpage_from_qibuild.py doc/qitoolchain-manpage.txt build-doc/qitoolchain-manpage.txt "qitoolchain.actions"

find build-doc/ -type f -name '*.txt' | while read f ; do
  #asciidoc is stupid about css...
  #we desactivated default theme, set the stylesheet to bare.css, and disable embedded css
  asciidoc.py -a toc -a toclevels=1  -a linkcss -a 'theme=' -a stylesheet="bare.css" -a pygments "$f"
done

doc/tools/generate_examples_archive python/qibuild/test/ "build-doc"
