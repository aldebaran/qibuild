include_directories(${CMAKE_CURRENT_SOURCE_DIR})

qi_create_lib(foo
  SRC foo/foo.h
      foo/foo.cpp
      foo/src/foo_private.h
      foo/src/foo_private.cpp
  SUBFOLDER
      foo
)

qi_stage_lib(foo)
