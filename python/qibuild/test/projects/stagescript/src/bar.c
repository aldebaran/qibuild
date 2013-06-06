

#ifdef _WIN32
__declspec(dllimport)
#endif
int foo(int);

#ifdef _WIN32
__declspec(dllexport)
#endif
int bar(int i) { return 1+foo(i);}

