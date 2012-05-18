include_directories(".")

qi_create_lib(foo
  SRC foo/foo.hpp
      foo/foo.cpp
      src/foo_private.hpp
      src/foo_private.cpp
  SHARED
)


# Add dependencies to the foo library here:
# qi_use_lib(foo ... )

qi_install_header(KEEP_RELATIVE_PATHS foo/foo.hpp)

qi_stage_lib(foo)

add_subdirectory(test)
