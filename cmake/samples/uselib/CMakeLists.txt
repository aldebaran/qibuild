

project(UseLibSample)

include(${CMAKE_CURRENT_SOURCE_DIR}/foosdk/sourceme.cmake)

#set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH}" "${CMAKE_CURRENT_SOURCE_DIR}/mycmakeproject1")
#set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/mycmakeproject1/share/cmake/")

message("CMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}")
message("CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}")

find_package(Foo)
