include_directories("${CMAKE_SOURCE_DIR}/libbar")

add_executable(foo main.cpp)
target_link_libraries(foo bar)

install(TARGETS foo DESTINATION "bin")
