cmake_minimum_required(VERSION 2.8)
project(cov)

find_package(qibuild)
qi_sanitize_compile_flags()
# Create a executable named cov
# with the source file: main.cpp
qi_create_bin(cov "main.cpp")

# Add a simple test:
enable_testing()
qi_create_test(test_cov "test.cpp")
