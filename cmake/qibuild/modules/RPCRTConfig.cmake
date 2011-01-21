##
## Copyright (C) 2008 Aldebaran Robotics



clean(RPCRT)

# Note the space is important, we need to set it to something!
set(RPCRT_INCLUDE_DIR " " CACHE STRING "" FORCE)
set(RPCRT_LIBRARIES "Rpcrt4" CACHE STRING "" FORCE)
export_lib(RPCRT)
