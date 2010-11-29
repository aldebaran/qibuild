##
## Copyright (C) 2008 Aldebaran Robotics



clean(WSA)
# winsock2.h requires with ws2_32.lib
# 
# Note the space is important, we need to set it to something!
set(WSA_INCLUDE_DIR " " CACHE STRING "" FORCE)
set(WSA_LIBRARIES "ws2_32" CACHE STRING "" FORCE)
export_lib(WSA)

