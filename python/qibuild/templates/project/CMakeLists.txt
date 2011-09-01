cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(@project_name@)

include("qibuild.cmake")

# Create a executable
qi_create_bin(@project_name@ "main.cpp")

# Just a quick test to be sure the executable can run.
enable_testing()
qi_add_test(zero_test @project_name@)

