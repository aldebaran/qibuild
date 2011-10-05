cmake_minimum_required(VERSION 2.8)

# Give a name to the project.
project(@project_name@)

# You need this to find the QiBuild CMake framework
include("qibuild.cmake")

# Create a executable named @project_name@
# with the source file: main.cpp
qi_create_bin(@project_name@ "main.cpp")

# Just a quick test to be sure the executable can run.
enable_testing()
qi_add_test(zero_test @project_name@)

