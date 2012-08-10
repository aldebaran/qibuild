include_directories(".")

qi_create_lib(foo
  SRC foo/foo.hpp
      src/foo.cpp
      src/foo_p.hpp
      src/foo_p.cpp
  SHARED
)


# Add dependencies to the foo library here:
# qi_use_lib(foo ... )

qi_install_header(KEEP_RELATIVE_PATHS foo/foo.hpp)

qi_stage_lib(foo)

add_subdirectory(test)
