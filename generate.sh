#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

CURDIR=$(dirname "$(readlink -f $0 2>/dev/null)")/


python ${CURDIR}/doc/tools/generate_doc_from_cmake.py \
  "${CURDIR}/cmake/qibuild" \
  "${CURDIR}/cmake/samples" \
  "${CURDIR}/build-doc-pre"

cp "${CURDIR}/doc/asciidoc/index.txt" "${CURDIR}/build-doc-pre"

find ${CURDIR}/build-doc-pre/ -type f -name '*.txt' | while read f ; do
  #asciidoc -a toc -a theme=bare -a pygments "$f"
  #asciidoc -a toc -a linkcss -a theme=bare -a pygments "$f"
  asciidoc -a toc -a toclevels=1 -a linkcss -a theme= -a stylesheet=bare.css -a pygments "$f"
done

