include_directories(".")

add_library(bar
  bar/bar.hpp
  bar/bar.cpp)

install(TARGETS bar
  RUNTIME DESTINATION "lib"
  ARCHIVE DESTINATION "lib"
  LIBRARY DESTINATION "lib")

install(FILES bar/bar.h
  DESTINATION "include/bar")
