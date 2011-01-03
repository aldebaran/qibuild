#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

#Create a simple launcher for QiBuild. It will install in /usr/local/bin.

DESTDIR="/usr/local/bin"

create_launcher() {
  full_path=$1
  name=$(basename $full_path)
  if which readlink >/dev/null 2>/dev/null ; then
      p=$(dirname "$(readlink -f $0 2>/dev/null)")
  else
      p=$(pwd)
  fi
  #echo "QiBuild directory: $p"

  echo '#!/bin/sh'                                                         > ${DESTDIR}/${name}
  echo "PYTHONPATH=\"$p/python:${PYTHONPATH}\" python \"${p}/${full_path}\" \$@" >> ${DESTDIR}/${name}
  chmod 755 ${DESTDIR}/${name}

  echo "installed: ${DESTDIR}/${name}"
}

mkdir -p ${DESTDIR}
create_launcher bin/qibuild
create_launcher bin/qitoolchain
create_launcher bin/qisrc
