##
# Copyright (C) 2010 Aldebaran Robotics
#


add_executable(foo main.cpp)

qi_use_lib(foo bar)


install(TARGETS foo DESTINATION "bin")
