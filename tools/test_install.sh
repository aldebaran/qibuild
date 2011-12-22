#!/bin/bash -xe
rm -fr /tmp/qibuild
rm -fr ../b
mkdir ../b
cd ../b
cmake ..
DESTDIR=/tmp/qibuild make install
pushd /tmp/qibuild/usr/local/bin
PYTHONPATH=/tmp/qibuild/usr/local/lib/python2.7/site-packages/ ./qibuild init
PYTHONPATH=/tmp/qibuild/usr/local/lib/python2.7/site-packages/ ./qibuild create foo
PYTHONPATH=/tmp/qibuild/usr/local/lib/python2.7/site-packages/ ./qibuild configure foo
rm /tmp/qibuild/usr/local/bin/foo/qibuild.cmake
PYTHONPATH=/tmp/qibuild/usr/local/lib/python2.7/site-packages/ ./qibuild convert foo
PYTHONPATH=/tmp/qibuild/usr/local/lib/python2.7/site-packages/ ./qibuild configure foo
popd
cd ..
rm -fr b

