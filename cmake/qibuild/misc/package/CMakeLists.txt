# install a correctly configured
# toolchain-pc.cmake at the root of the
# SDK


configure_file(toolchain-pc.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/toolchain-pc.cmake"
  @ONLY)

install( FILES
    "${CMAKE_CURRENT_BINARY_DIR}/toolchain-pc.cmake"
  COMPONENT "cmake"
  DESTINATION
    "."
)
