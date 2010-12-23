#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#this script will install naogentoo, toc, on, dorelease

DESTDIR="/usr/local/bin"

create_launcher() {
  full_path=$1
  name=$(basename $full_path)
  if which readlink ; then
      p=$(dirname "$(readlink -f $0 2>/dev/null)")
  else
      p=$(pwd)
  fi
  echo "QiBuild directory: $p"

  echo '#!/bin/sh'                                           > ${DESTDIR}/${name}
  echo "PYTHONPATH=\"$p\" python \"${p}/${full_path}\" \$@" >> ${DESTDIR}/${name}
  chmod 755 ${DESTDIR}/${name}
}

mkdir -p ${DESTDIR}
create_launcher bin/qibuild
