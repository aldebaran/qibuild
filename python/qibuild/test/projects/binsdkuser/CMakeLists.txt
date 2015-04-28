cmake_minimum_required(VERSION 2.8)
project(binsdkuser)

find_package(qibuild)

find_package(FOO)
if(NOT EXISTS ${FOO_LIBRARIES})
  qi_error("FOO_LIBRARIES: ${FOO_LIBRARIES} does not exist")
endif()
