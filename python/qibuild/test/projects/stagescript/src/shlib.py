## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def load_shlib(name, verbose=False):
  """ Load a shared library, try to handle as many cases as possible
  """
  import ctypes
  import os
  import sys
  medir = os.path.dirname(os.path.abspath(__file__))
  if verbose:
    print("PATH: " + os.environ.get('PATH', ''))
    print("LD_LIBRARY_PATH: " + os.environ.get('LD_LIBRARY_PATH', ''))
    print("DYLD_LIBRARY_PATH: " + os.environ.get('DYLD_LIBRARY_PATH', ''))
  if sys.platform.startswith('linux'):
    soname = [".so"]
    prefix = "lib"
    paths = ['', '../lib', os.path.join(medir, '..', 'lib')]
  elif sys.platform.startswith('darwin'):
    soname = [".dylib"]
    prefix = "lib"
    paths = ['', '../lib', os.path.join(medir, '..', 'lib')]
  else:
    # Windows has no RPATH equivalent, but allows for changing the
    # search path within the process.
    ctypes.windll.kernel32.SetDllDirectoryA(os.path.join(medir))
    soname = [".dll", "_d.dll"]
    prefix = ''
    paths = ['', '.', os.path.join(medir, '..', 'lib'), os.path.join(medir, '..', 'bin')]

  if verbose:
    print("Loading " + name)
  handle = None
  for s in soname:
    for p in paths:
      path = os.path.join(p, prefix + name + s)
      try:
        handle = ctypes.cdll.LoadLibrary(path)
        break
      except Exception as e:
        if verbose:
          print(path + " : " + str(e))
  return handle

