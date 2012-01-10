#!/bin/sh
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

# Create a simple launcher for QiBuild scipts.
# They will install in /usr/local/bin, but
# sources will stay where they are.

DESTDIR="/usr/local/bin"


create_launcher() {
  full_path="$1"
  name="$2"
  shift
  shift
  args="$@"

  if readlink -f . >/dev/null 2>/dev/null ; then
      p=$(dirname "$(readlink -f '$0' 2>/dev/null)")
  else
      p=$(pwd)
  fi
  #echo "QiBuild directory: $p"

  echo '#!/bin/sh'                                                     >  "${DESTDIR}/${name}"
  echo "PYTHONPATH=\"$p/python\" python \"${p}/${full_path}\" $args \"\$@\"" >> "${DESTDIR}/${name}"
  chmod 755 "${DESTDIR}/${name}"
  echo "installed: ${DESTDIR}/${name}"
}


localinst=no
if ! mkdir -p "${DESTDIR}" 2>/dev/null ; then
  localinst=yes
fi

if ! touch "${DESTDIR}"/.tmp_test ; then
  localinst=yes
else
  rm -f "${DESTDIR}/.tmp_test"
fi

if [ "$localinst" = "yes" ] ; then
  echo WARNING: ${DESTDIR} is not writable
  echo =====================
  echo installing into ~/bin
  echo You should add ~/bin to your PATH
  echo =====================
  echo
  DESTDIR=~/bin
  mkdir -p "${DESTDIR}"
fi

create_launcher python/bin/qibuild      qibuild
create_launcher python/bin/qitoolchain  qitoolchain
create_launcher python/bin/qisrc        qisrc
create_launcher python/bin/qidoc        qidoc

#aliases
create_launcher python/bin/qibuild      qc           configure
create_launcher python/bin/qibuild      qm           make
create_launcher python/bin/qisrc        qp           pull --rebase
create_launcher python/bin/qibuild      qo           open
