## Copyright (C) 2011 Aldebaran Robotics


include(CMakeParseArguments)

#! Python wrapper for swig.
#
# /!\ The module_name must be the same as the one declare in ${interface_file}
# for instance, if module_name equals foo, foo.i must contain:
#   %module foo
#
# \arg:module_name the target name
# \arg:interface_file the swig interface file (extension is .i)
# \group:SRC The list of source files
# \group:DEPENDS The list of source files
function(qi_swig_wrap_python module_name interface_file)
  cmake_parse_arguments(ARG "" "" "SRC;DEPENDS" ${ARGN})

  # we search for the SWIG_EXECUTABLE by yourself, because FindSWIG call find_file
  # but when we are cross-compiling and we want to use swig from the system
  # then CMAKE_FIND_ROOT_PATH prevent find_file from working.
  find_program(SWIG_EXECUTABLE swig)
  if(NOT SWIG_EXECUTABLE)
    qi_error("Could not find swig executable in PATH, python wrapping is disabled")
  endif()

  include("UseSWIG")
  #find_package(SWIG REQUIRED)
  #include(${SWIG_USE_FILE})

  set_source_files_properties(${interface_file} PROPERTIES CPLUSPLUS ON)
  # tell swig that the generated module name is ${module_name}.py
  # without this property, it assumes that it is ${interface_file}.py
  # TODO: check that it is a correct way to do this and not a nifty hack
  set_source_files_properties(
    ${interface_file} PROPERTIES SWIG_MODULE_NAME "${module_name}")


  # Everything will end up in ${SDK_DIR}/${SDK_DIR}, so that
  # setting PYTHONPATH and LD_LIBRARY_PATH (or PATH) is enough
  set(CMAKE_SWIG_OUTDIR ${QI_SDK_DIR}/${QI_SDK_LIB})

  ##
  # Deal with dependencies:
  foreach (_dep ${ARG_DEPENDS})
    find_package(${_dep} NO_MODULE QUIET)
    find_package(${_dep} REQUIRED)
    include_directories(
      ${${_dep}_INCLUDE_DIR}
      ${${_dep}_INCLUDE_DIRS})
  endforeach()

  find_package(PYTHON)
  include_directories(${PYTHON_INCLUDE_DIR})
  # Since there is often a "lazy" include in the interface file:
  include_directories(${CMAKE_CURRENT_SOURCE_DIR})

  swig_add_module(${module_name} python ${interface_file} ${ARG_SRC})

  ##
  # Deal with the newly created target

  # Store the target created by swig_add_module in a more friendly name:
  set(_swig_target ${SWIG_MODULE_${module_name}_REAL_NAME})

  qi_use_lib(${_swig_target} PYTHON ${ARG_DEPENDS})

  set_target_properties(${_swig_target}
    PROPERTIES
      LIBRARY_OUTPUT_DIRECTORY "${QI_SDK_DIR}/${QI_SDK_LIB}"
  )

  if (WIN32)
  # Be sure a .pyd file gets created.
    set_target_properties(${_swig_target}
      PROPERTIES
        SUFFIX   ".pyd"
        RUNTIME_OUTPUT_DIRECTORY "${QI_SDK_DIR}/${QI_SDK_BIN}"
    )

    if(MSVC)
      # .dll compiled in debug with visual studio are not usable
      # from python.exe, (unless you are very careful : the size of the ojbjects
      # are not the same in debug or in release with visual studio), which
      # can lead to hard to solve bugs.
      # Here, we add an _d so we are sure a Visual Studio users cannot
      # use their modules unless they have built them in release.
      set_target_properties(${_swig_target}
        PROPERTIES
          DEBUG_POSTFIX "_d"
      )
    endif()
  endif()

  # Re-create install rules:
  install(TARGETS ${_swig_target}
    COMPONENT python
    LIBRARY DESTINATION "${QI_SDK_LIB}"
    RUNTIME DESTINATION "${QI_SDK_LIB}"
  )

  install(FILES "${QI_SDK_DIR}/${QI_SDK_LIB}/${module_name}.py"
    COMPONENT python
    DESTINATION "${QI_SDK_LIB}"
  )


endfunction()
