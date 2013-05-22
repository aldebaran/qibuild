#!/bin/sh
## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
##

# Create a simple launcher for QiBuild scipts.
# They will install in /usr/local/bin, but
# sources will stay where they are.
# Note: on distros where /usr/bin/python is Python 3, you should
# set PYTHON env var to python2

DESTDIR="/usr/local/bin"


create_launcher() {
  full_path="$1"
  name="$2"
  shift
  shift
  args="$@"

  if [ -z $PYTHON ]; then
    PYTHON=python
  fi

  if readlink -f . >/dev/null 2>/dev/null ; then
      p=$(dirname "$(readlink -f ${0} 2>/dev/null)")
  else
      p=$(dirname "${0}")
      p=$PWD/$p
  fi
  #echo "QiBuild directory: $p"

  cat <<EOF >"${DESTDIR}/${name}"
#!/bin/sh

python "${p}/${full_path}" ${args} "\$@"
EOF
  chmod 755 "${DESTDIR}/${name}"
  echo "Installed: ${DESTDIR}/${name}"
}


localinst=no
if ! mkdir -p "${DESTDIR}" 2>/dev/null ; then
  localinst=yes
fi

if ! touch "${DESTDIR}"/.tmp_test 2>/dev/null ; then
  localinst=yes
else
  rm -f "${DESTDIR}/.tmp_test"
fi

if [ "$localinst" = "yes" ] ; then
  echo WARNING: ${DESTDIR} is not writable
  echo =====================
  echo installing into ~/.local/bin
  echo You should add ~/.local/bin to your PATH
  echo =====================
  echo
  DESTDIR=~/.local/bin
  mkdir -p "${DESTDIR}"
fi

create_launcher python/bin/qibuild      qibuild
create_launcher python/bin/qitoolchain  qitoolchain
create_launcher python/bin/qisrc        qisrc
create_launcher python/bin/qidoc        qidoc
create_launcher python/bin/qilinguist   qilinguist
create_launcher python/bin/qicd.py      qicd.py

#aliases
create_launcher python/bin/qibuild      qc           configure
create_launcher python/bin/qibuild      qd           deploy
create_launcher python/bin/qibuild      qm           make
create_launcher python/bin/qibuild      qo           open
echo "Make sure ${DESTDIR} is in your PATH."
