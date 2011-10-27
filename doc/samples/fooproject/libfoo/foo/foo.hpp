#ifndef _FOO_HPP_
#define _FOO_HPP_

// For shared library
#if defined _WIN32 || defined __CYGWIN__
#  define _EXPORT_API __declspec(dllexport)
#  if defined _WINDLL
#    define _IMPORT_API __declspec(dllimport)
#  else
#    define _IMPORT_API
#  endif
#elif __GNUC__ >= 4
#  define _EXPORT_API __attribute__ ((visibility("default")))
#  define _IMPORT_API __attribute__ ((visibility("default")))
#else
#  define _EXPORT_API
#  define _IMPORT_API
#endif


// foo_EXPORTS controls which symbols are exported when libqi
// is compiled as a SHARED lib.
// DO NOT USE OUTSIDE libfoo, and make sure the prefix
// of _EXPORTS define matches the CMake target name
#ifdef foo_EXPORTS
# define FOO_API _EXPORT_API
#elif defined(foo_IMPORTS)
# define FOO_API _IMPORT_API
#else
# define FOO_API
#endif


FOO_API int public_method();

#endif // _FOO_HPP_
