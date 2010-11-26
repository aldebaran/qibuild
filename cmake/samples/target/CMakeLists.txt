##
## target examples
##


project(SampleTarget)


qi_create_bin(myprog SRC main.cpp)
qi_create_lib(mylib SRC mylib.h mylib.c)
