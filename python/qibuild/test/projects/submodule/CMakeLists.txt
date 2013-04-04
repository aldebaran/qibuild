cmake_minimum_required(VERSION 2.8)
project(submodule)

find_package(qibuild)

set(BUILTIN TRUE)

qi_submodule_add(sm SRC hello.h hello.cpp)
if(BUILTIN)
  qi_submodule_add(sm SRC say.cpp say.h)
else()
  qi_create_lib(say say.cpp say.h)
  qi_submodule_add(sm SRC say.h DEPENDS say)
endif()
qi_create_bin(submodule SRC main.cpp SUBMODULE sm)
