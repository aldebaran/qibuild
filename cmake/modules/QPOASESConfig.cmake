include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(QPOASES)

fpath(QPOASES QProblem.hpp PATH_SUFFIXES qpoases)
flib(QPOASES qpoases)
export_lib(QPOASES)
