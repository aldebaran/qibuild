##
## target examples
##


project(SampleTarget)

#add_subdirectory(fooscript)
add_subdirectory(foolib)
add_subdirectory(foobin)

qi_create_bin(myprog SRC main.cpp)
qi_create_lib(mylib SRC mylib.h mylib.c)
