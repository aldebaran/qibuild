#pragma once

// Usual crap for shared libraries on Windows ...
#ifdef WIN32
#  ifdef foo_EXPORTS
#    define FOO_API   __declspec( dllexport )
#  else
#    define FOO_API  __declspec( dllimport )
#  endif
#else
#  define FOO_API
#endif

FOO_API int foo();
