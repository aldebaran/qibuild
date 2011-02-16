##
# Copyright (C) 2010 Aldebaran Robotics
#

include_directories(${CMAKE_SOURCE_DIR}/bar)

add_executable(foo main.cpp)

target_link_libraries(foo bar)

install(TARGETS foo DESTINATION "bin")
