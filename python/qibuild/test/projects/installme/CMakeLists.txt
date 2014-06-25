cmake_minimum_required(VERSION 2.8)
project(installme)

find_package(qibuild)

qi_install_data(data/* SUBFOLDER data_star)

# relative paths
qi_install_header(relative/foo/foo.h relative/bar/bar.h
  KEEP_RELATIVE_PATHS)

# recurse
qi_install_data(recurse/*
  RECURSE KEEP_RELATIVE_PATHS)

if (FAIL_EMPTY_GLOB)
  qi_install_data(nonexisting/*)
endif()

if (FAIL_NON_EXISTING)
  qi_install_data(nonexisting)
endif()

# test
qi_create_test_lib(foo foo.cpp)
qi_install_test_data(test_data.dat)
