#ifndef _PLUGIN_H
#define _PLUGIN_H

#ifdef WIN32
#  ifdef myplugin_EXPORTS
#    define MYPLUGIN_API   __declspec( dllexport )
#  else
#    define MYPLUGIN_API  __declspec( dllimport )
#  endif
#else
#  define MYPLUGIN_API
#endif

MYPLUGIN_API int load_plugin();

#endif // _PLUGIN_H
