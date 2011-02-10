## Copyright (C) 2011 Aldebaran Robotics
include("${TOOLCHAIN_DIR}/cmake/plateform.cmake")

if (WIN32)
set (CMAKE_SYSTEM_NAME "linux")
endif()

if (NOT OE_CROSS_DIR)
  message(STATUS
    "\n"
    "===========================================================\n"
    "= No cross-toolchain folder specified                     =\n"
    "= Correct OE_CROSS_DIR in your toolchain file             =\n"
    "= Please refer to the T001chain doc                       =\n"
    "===========================================================\n"
    )
  message(FATAL_ERROR "")
endif()


include(CMakeForceCompiler)

set(OE_CROSS_BUILD ON)
set(OE_PREFIX "geode-linux" )
set(OE_ARCH   "i586-linux" )
if (WIN32)
	set(OE_ARCH   "i586-nao-linux-gnu" )
endif()


#cross-compiling: dont use system libraries at all
set(INCLUDE_EXTRA_PREFIX "" CACHE INTERNAL "" FORCE)
set(LIB_EXTRA_PREFIX     "" CACHE INTERNAL "" FORCE)

#standard library path:
#where to search for bin, library and include
set(BIN_PREFIX     "${OE_CROSS_DIR}/staging/${OE_PREFIX}/usr/bin/"     CACHE INTERNAL "" FORCE)
set(INCLUDE_PREFIX "${OE_CROSS_DIR}/staging/${OE_PREFIX}/usr/include/" CACHE INTERNAL "" FORCE)
set(LIB_PREFIX     "${OE_CROSS_DIR}/staging/${OE_PREFIX}/usr/lib/"     CACHE INTERNAL "" FORCE)

# root of the cross compiled filesystem
#should be set but we do find_path in each module outside this folder !!!!
#set(CMAKE_FIND_ROOT_PATH  ${OE_CROSS_DIR}/staging/${OE_PREFIX}/ ${OE_CROSS_DIR}/cross)
# search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY)
# for libraries and headers in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(OE_CROSS "${OE_CROSS_DIR}/cross/geode")
if (WIN32)
	set(OE_CROSS "${OE_CROSS_DIR}/cross/nao-cross")
endif()
set(OE_STAGE "${OE_CROSS_DIR}/staging/${OE_PREFIX}")

#avoid checking the compiler is OK (wont work with good CFLAGS/CXXFLAGS)
#we dont want to use cross-compile.sh or other script to call cmake with good flags defined


CMAKE_FORCE_C_COMPILER(  "${OE_CROSS}/bin/${OE_ARCH}-gcc" GNU)
CMAKE_FORCE_CXX_COMPILER("${OE_CROSS}/bin/${OE_ARCH}-g++" GNU)
if (WIN32)
CMAKE_FORCE_C_COMPILER(  "${OE_CROSS}/bin/${OE_ARCH}-gcc.exe" GNU)
CMAKE_FORCE_CXX_COMPILER("${OE_CROSS}/bin/${OE_ARCH}-g++.exe" GNU)
endif()

# disable for more stability (yes cmake is crappy sometime) see =>
#http://www.cmake.org/Wiki/CMake_FAQ#I_change_CMAKE_C_COMPILER_in_the_GUI_but_it_changes_back_on_the_next_configure_step._Why.3F
set(CMAKE_AR           "${OE_CROSS}/bin/${OE_ARCH}-ar"      CACHE FILEPATH "" FORCE)
set(CMAKE_RANLIB       "${OE_CROSS}/bin/${OE_ARCH}-ranlib"  CACHE FILEPATH "" FORCE)

if (WIN32)
set(CMAKE_AR           "${OE_CROSS}/bin/${OE_ARCH}-ar.exe"      CACHE FILEPATH "" FORCE)
set(CMAKE_RANLIB       "${OE_CROSS}/bin/${OE_ARCH}-ranlib.exe"  CACHE FILEPATH "" FORCE)
endif()

# If ccache is found, just use it:)
if (NOT WIN32)
find_program(CCACHE "ccache")
if (CCACHE)
  message( STATUS "Using ccache")
endif()
if (CCACHE AND NOT FORCE_NO_CCACHE)
  set(CMAKE_C_COMPILER         ${CCACHE} CACHE FILEPATH "" FORCE)
  set(CMAKE_CXX_COMPILER       ${CCACHE} CACHE FILEPATH "" FORCE)
  set(CMAKE_C_COMPILER_ARG1   "${OE_CROSS}/bin/${OE_ARCH}-gcc" CACHE FILEPATH "" FORCE)
  set(CMAKE_CXX_COMPILER_ARG1 "${OE_CROSS}/bin/${OE_ARCH}-g++" CACHE FILEPATH "" FORCE)
else()
  set(CMAKE_C_COMPILER   "${OE_CROSS}/bin/${OE_ARCH}-gcc"     CACHE FILEPATH "" FORCE)
  set(CMAKE_CXX_COMPILER "${OE_CROSS}/bin/${OE_ARCH}-g++"     CACHE FILEPATH "" FORCE)
endif()
endif()


set(X86_GCCLIB_DIR     "${OE_CROSS}/lib/gcc/${OE_ARCH}/4.3.3/" )
set(X86_GINCLUDE_DIR   "${OE_CROSS}/lib/gcc/${OE_ARCH}/4.3.3/include/" )
set(X86_GLIBC_DIR      "${OE_CROSS}/${OE_ARCH}/lib/" )
set(X86_GCCINC_DIR     "${OE_CROSS}/${OE_ARCH}/include/" )
set(X86_GPPINC_DIR     "${OE_CROSS}/${OE_ARCH}/include/c++/" )
set(X86_GPPINC2_DIR    "${OE_CROSS}/${OE_ARCH}/include/c++/backward/" )
set(X86_GPPINC3_DIR    "${OE_CROSS}/${OE_ARCH}/include/c++/${OE_ARCH}" )
set(X86_LDLINUXSO_DIR  "${OE_STAGE}/lib/" )
set(X86_INCLUDE_DIR    "${OE_STAGE}/usr/include/" )
set(X86_CPINCLUDE_DIR  "${OE_STAGE}/usr/include/c++/" )
set(X86_GCPINCLUDE_DIR "${OE_STAGE}/usr/include/c++/${OE_ARCH}/" )

if (WIN32)
set(X86_GCCLIB_DIR     "${OE_CROSS}/lib/gcc/${OE_ARCH}/4.4.1/" )
set(X86_GINCLUDE_DIR   "${OE_CROSS}/lib/gcc/${OE_ARCH}/4.4.1/include/" )
set(X86_GLIBC_DIR      "${OE_CROSS}/${OE_ARCH}/lib/" )
set(X86_GCCINC_DIR     "${OE_CROSS}/${OE_ARCH}/include/" )
set(X86_GPPINC_DIR     "${OE_CROSS}/${OE_ARCH}/include/c++/" )
set(X86_GPPINC2_DIR    "${OE_CROSS}/${OE_ARCH}/include/c++/backward/" )
set(X86_GPPINC3_DIR    "${OE_CROSS}/${OE_ARCH}/include/c++/${OE_ARCH}" )
set(X86_LDLINUXSO_DIR  "${OE_STAGE}/lib/" )
set(X86_INCLUDE_DIR    "${OE_STAGE}/usr/include/" )
set(X86_CPINCLUDE_DIR  "${OE_STAGE}/usr/include/c++/" )
set(X86_GCPINCLUDE_DIR "${OE_STAGE}/usr/include/c++/${OE_ARCH}/" )
endif()

set(CMAKE_C_FLAGS "--sysroot ${OE_STAGE}/ -I${X86_INCLUDE_DIR} -I${X86_GINCLUDE_DIR} -I${X86_CPINCLUDE_DIR} -I${X86_GCPINCLUDE_DIR} -I${X86_GPPINC_DIR} -I${X86_GPPINC2_DIR} -I${X86_GPPINC3_DIR} -I${X86_GCCINC_DIR} -march=geode" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS}" CACHE STRING "" FORCE)
set(CMAKE_EXE_LINKER_FLAGS "-Wl,--sysroot,${OE_STAGE}/ -lgcc -L${X86_GLIBC_DIR} -lc -lstdc++ -ldl" CACHE STRING "" FORCE)

add_definitions(-march=geode)
