cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(@project_name@)

include("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")

# Create a executable
qi_create_bin(@project_name@ "main.cpp")

enable_testing()

# Just a quick test to be sure the executable can run.
add_test(zero_test ${CMAKE_BINARY_DIR}/sdk/${QI_SDK_BIN}/@project_name@)

