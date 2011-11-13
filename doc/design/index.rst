.. _qibuild-design:

QiBuild framework design
========================

CMake
-----


* General design decision:
  - close to standard
  - use toolchain files
  - SDK layout

* Implementation:
  - search order
  - Glue with ``qibuild`` command line: qibuild.cmake, dependencies.cmake
  - handling dynamic libraries


Python
------


* DRY

* Modular design: one executable per task

* Toc and Worktree:
  - dependency resolution
  - projects search

* cmake flags handling

* config hanlding:
  - configstore stuff
  - config.get(..., config=None)

* Toolchain and packages handling:
  - feed parsing
  - cache


