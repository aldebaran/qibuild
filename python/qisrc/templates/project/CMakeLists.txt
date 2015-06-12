cmake_minimum_required(VERSION 2.8)
project(@project_name@)

find_package(qibuild)

# Create a executable named @project_name@
# with the source file: main.cpp
qi_create_bin(@project_name@ "main.cpp")

# Add a simple test:
qi_create_test(test_@project_name@ "test.cpp")
